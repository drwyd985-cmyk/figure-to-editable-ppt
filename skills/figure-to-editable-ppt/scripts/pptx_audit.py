#!/usr/bin/env python3
"""Read-only PPTX inventory and approved-native-text regression audit.

Standard library only. This tool does not render, OCR, or prove visual fidelity.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import posixpath
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile


def local(tag):
    return tag.rsplit('}', 1)[-1]


def digest(data):
    return sha256(data).hexdigest()


def structure(el, omit_identity=False):
    if el is None:
        return None
    attrs = dict(el.attrib)
    if omit_identity and local(el.tag) == 'cNvPr':
        attrs.pop('id', None)
    # Expanded namespace tags and sorted attributes avoid prefix-only changes.
    text = el.text if local(el.tag) == 't' else (el.text or '').strip()
    return [el.tag, sorted(attrs.items()), text,
            [structure(c, omit_identity) for c in el]]


def signature(el, omit_identity=False):
    data = json.dumps(structure(el, omit_identity), ensure_ascii=False,
                      separators=(',', ':')).encode('utf-8')
    return digest(data)


def resolve_part(owner, target):
    target = target.replace('\\', '/')
    part = posixpath.normpath(target.lstrip('/') if target.startswith('/')
                             else posixpath.join(posixpath.dirname(owner), target))
    if part == '..' or part.startswith('../') or ':' in part:
        raise ValueError('Relationship target is outside the package')
    return part


def read_xml(z, part):
    info = z.getinfo(part)
    if info.file_size > 64 * 1024 * 1024:
        raise ValueError('XML part exceeds the 64 MiB inspection limit: ' + part)
    data = z.read(part)
    if b'<!DOCTYPE' in data.upper():
        raise ValueError('DTD declarations are not supported: ' + part)
    return ET.fromstring(data)


def relationships(z, owner):
    path = str(PurePosixPath(owner).parent / '_rels' /
               (PurePosixPath(owner).name + '.rels'))
    if path not in z.namelist():
        return {}
    result = {}
    for el in read_xml(z, path):
        external = el.get('TargetMode') == 'External'
        result[el.get('Id')] = {
            'type': el.get('Type'), 'external': external,
            'target': el.get('Target') if external else resolve_part(owner, el.get('Target', ''))}
    return result


def transform(el, ns, group=False):
    xf = el.find('p:grpSpPr/a:xfrm' if group else 'p:spPr/a:xfrm', ns)
    if xf is None:
        xf = el.find('p:xfrm', ns)
    if xf is None:
        return None
    return {'attributes': dict(xf.attrib),
            'coordinates': {local(c.tag): dict(c.attrib) for c in xf}}


def inventory(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    slides = []
    with ZipFile(path) as z:
        presentation = read_xml(z, 'ppt/presentation.xml')
        pns = presentation.tag.split('}')[0].lstrip('{')
        strict = pns == 'http://purl.oclc.org/ooxml/presentationml/main'
        if pns not in ('http://schemas.openxmlformats.org/presentationml/2006/main',
                       'http://purl.oclc.org/ooxml/presentationml/main'):
            raise ValueError('Unsupported presentation namespace: ' + pns)
        ns = {'p': pns,
              'a': 'http://purl.oclc.org/ooxml/drawingml/main' if strict else 'http://schemas.openxmlformats.org/drawingml/2006/main',
              'r': 'http://purl.oclc.org/ooxml/officeDocument/relationships' if strict else 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        presrels = relationships(z, 'ppt/presentation.xml')
        size = presentation.find('p:sldSz', ns)
        slide_ids = presentation.find('p:sldIdLst', ns)
        if size is None or slide_ids is None or not len(slide_ids):
            raise ValueError('Presentation has no slide size or slide list')
        for index, link in enumerate(slide_ids, 1):
            rel = presrels[link.get('{'+ns['r']+'}id')]
            if rel['external']:
                raise ValueError('External slide parts are not supported')
            part = rel['target']; root = read_xml(z, part)
            rels = relationships(z, part)
            entries = []

            def walk(tree, ancestors):
                for el in tree:
                    kind = local(el.tag)
                    if kind not in ('sp', 'pic', 'cxnSp', 'grpSp', 'graphicFrame'):
                        continue
                    nv = next((c for c in el.iter() if local(c.tag) == 'cNvPr'), None)
                    if nv is None:
                        raise ValueError('Drawable object lacks cNvPr in ' + part)
                    xf = transform(el, ns, kind == 'grpSp')
                    bodies = el.findall('p:txBody', ns)
                    if kind == 'graphicFrame':
                        bodies += [c for c in el.iter() if local(c.tag) == 'txBody']
                    paragraphs = [p for b in bodies for p in b.findall('a:p', ns)]
                    value = '\n'.join(''.join(p.itertext()).strip() if not p.findall('.//a:t', ns)
                                      else ''.join(t.text or '' for t in p.findall('.//a:t', ns))
                                      for p in paragraphs)
                    entry = {'id': nv.get('id'), 'name': nv.get('name', ''),
                             'kind': kind, 'text': value, 'transform': xf,
                             'ancestor_group_transforms': ancestors,
                             'node_count': sum(local(c.tag) in ('moveTo', 'lnTo', 'cubicBezTo', 'quadBezTo') for c in el.iter()) if kind != 'grpSp' else 0}
                    if kind != 'grpSp':
                        entry['solid_fills'] = [c.get('val') for c in el.findall('p:spPr/a:solidFill/a:srgbClr', ns)]
                        entry['stroke'] = [structure(c) for c in el.findall('p:spPr/a:ln', ns)]
                    if value:
                        entry['object_sha256'] = signature(el)
                        entry['object_without_id_sha256'] = signature(el, True)
                        entry['text_style_sha256'] = digest(json.dumps([structure(b) for b in bodies], ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
                    if kind == 'pic':
                        entry['crop'] = [dict(c.attrib) for c in el.findall('p:blipFill/a:srcRect', ns)]
                        entry['media'] = []
                        for c in el.iter():
                            if local(c.tag) not in ('blip', 'svgBlip'):
                                continue
                            rid = c.get('{'+ns['r']+'}embed') or c.get('{'+ns['r']+'}link')
                            if rid in rels:
                                media = dict(rels[rid]); media['relationship_id'] = rid
                                if not media['external']:
                                    media['extension'] = PurePosixPath(media['target']).suffix.lower()
                                entry['media'].append(media)
                    entries.append(entry)
                    if kind == 'grpSp':
                        walk(el, ancestors + [xf])
            tree = root.find('p:cSld/p:spTree', ns)
            if tree is None:
                raise ValueError('Slide has no shape tree: ' + part)
            walk(tree, [])
            fills = [f for e in entries for f in e.get('solid_fills', [])]
            slides.append({'number': index, 'part': part,
                           'counts': dict(Counter(e['kind'] for e in entries)),
                           'native_text_objects': sum(bool(e['text']) for e in entries),
                           'distinct_explicit_solid_rgb_fills': len(set(fills)),
                           'objects': entries})
        media = [{'part': n, 'bytes': z.getinfo(n).file_size}
                 for n in z.namelist() if n.startswith('ppt/media/') and not n.endswith('/')]
    return {'file': str(path), 'sha256': digest(raw),
            'slide_size_emu': {k: int(size.get(k)) for k in ('cx', 'cy')},
            'slide_count': len(slides), 'media': media, 'slides': slides,
            'claim_boundary': 'Native package inventory only. No OCR, rendering, topology, visual fidelity, or editing-usability validation.'}


def extract_media(path, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('Media output must be a new directory: ' + str(destination))
    # Validate all input names before creating or writing anything.
    with ZipFile(path) as z:
        members = [i for i in z.infolist() if i.filename.startswith('ppt/media/') and not i.is_dir()]
        for item in members:
            parts = PurePosixPath(item.filename).parts
            if len(parts) != 3 or '..' in parts or '\\' in item.filename or ':' in item.filename:
                raise ValueError('Unsafe media member: ' + item.filename)
        destination.mkdir(parents=True)
        exported = []
        for i, item in enumerate(members, 1):
            target = destination / (str(i).zfill(4) + '_' + PurePosixPath(item.filename).name)
            target.write_bytes(z.read(item))
            exported.append({'part': item.filename, 'file': str(target)})
    return exported


def compare(before, after, prefix, match_by):
    def records(doc):
        answer = {}
        for slide in doc['slides']:
            for o in slide['objects']:
                if not o['text'] or not o['name'].startswith(prefix):
                    continue
                key = str(slide['number']) + '/' + str(o[match_by])
                if key in answer:
                    raise ValueError('Duplicate text match key: ' + key)
                answer[key] = o
        return answer
    b, a = records(before), records(after)
    if not b:
        raise ValueError('No native text matched the baseline; refusing an empty pass')
    changed = []
    sig = 'object_sha256' if match_by == 'id' else 'object_without_id_sha256'
    for key in sorted(b.keys() & a.keys()):
        fields = [field for field in ('text', 'text_style_sha256', 'transform', 'ancestor_group_transforms', sig)
                  if b[key].get(field) != a[key].get(field)]
        if fields:
            changed.append({'key': key, 'name': b[key]['name'], 'changed_fields': fields})
    missing = sorted(b.keys() - a.keys()); added = sorted(a.keys() - b.keys())
    canvas = before['slide_size_emu'] == after['slide_size_emu']
    pages = before['slide_count'] == after['slide_count']
    return {'baseline': before['file'], 'baseline_sha256': before['sha256'],
            'candidate': after['file'], 'candidate_sha256': after['sha256'],
            'match_by': match_by, 'name_prefix': prefix,
            'baseline_text_count': len(b), 'candidate_text_count': len(a),
            'same_canvas': canvas, 'same_slide_count': pages,
            'missing': missing, 'added': added, 'changed': changed,
            'passed': canvas and pages and not (missing or added or changed),
            'claim_boundary': 'Native text-object and ancestor-transform regression only; themes, layout inheritance, installed fonts, OCR, and visual appearance require separate review.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    a = sub.add_parser('inspect'); a.add_argument('pptx'); a.add_argument('--out', required=True); a.add_argument('--extract-media')
    a = sub.add_parser('compare-text'); a.add_argument('baseline'); a.add_argument('candidate')
    a.add_argument('--name-prefix', default=''); a.add_argument('--match-by', choices=('id', 'name'), default='id'); a.add_argument('--out', required=True)
    args = ap.parse_args()
    try:
        source_paths = [Path(args.pptx).resolve()] if args.command == 'inspect' else [Path(args.baseline).resolve(), Path(args.candidate).resolve()]
        out = Path(args.out).resolve()
        if out in source_paths:
            raise ValueError('Audit output must not overwrite an input PPTX')
        if args.command == 'inspect':
            report = inventory(args.pptx)
            if args.extract_media:
                report['extracted_media'] = extract_media(args.pptx, args.extract_media)
        else:
            report = compare(inventory(args.baseline), inventory(args.candidate), args.name_prefix, args.match_by)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        summary = {'report': str(out)}
        for key in ('passed', 'slide_count', 'baseline_text_count', 'candidate_text_count'):
            if key in report:
                summary[key] = report[key]
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if report.get('passed', True) else 1
    except (ValueError, KeyError, OSError, ET.ParseError, BadZipFile) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
