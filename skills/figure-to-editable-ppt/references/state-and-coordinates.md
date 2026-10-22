# 状态、坐标和可重复验证

## 恢复工作

在任务工作区保存状态文件，不把案例路径放进 skill：

```json
{
  "source": {"path": "<actual source>", "sha256": "<hash>", "slide_ids": []},
  "phase": "text_in_progress | text_review | geometry_in_progress | complete",
  "stage1": {
    "pptx": "<actual stage1 output>", "sha256": "<hash>", "preview": "<actual preview>",
    "review_status": "pending | approved | continuous_run_authorized",
    "authorization_basis": "<user instruction, not inferred from a validator>"
  },
  "stage2": {"pptx": null, "preview": null},
  "last_audit": {"scope": null, "report": null, "result": null},
  "pending_findings": [],
  "retained_raster_objects": []
}
```

用户说“继续”时先验证对应文件和哈希。新图建立新基线，不能套用上张图的尺寸、区域、字体或对象数。已有阶段2授权时直接恢复，不重复索取阶段1确认。

只读核查更新独立的 `last_audit` 或单独报告，不推断或改写现有重建阶段、确认状态。文字回归通过不代表图形已完成。

## 坐标

保留明确的源像素坐标系，每条记录说明 xywh 或 xyxy。画布来自实际文件；OOXML 使用 EMU，1 inch = 914400 EMU，1 point = 12700 EMU。仅在作者接口使用 CSS px 时才采用其换算。

无旋转/翻转、无祖先分组的图片，源尺寸 W/H、裁剪比例 l/t/r/b 的简式为：

```text
L = W*l, T = H*t
visibleW = W*(1-l-r), visibleH = H*(1-t-b)
x_slide = offX + (x_source-L)*pictureWidth/visibleW
y_slide = offY + (y_source-T)*pictureHeight/visibleH
```

srcRect 的 100000 表示 100%。旋转、翻转和分组需继续组合变换，不能直接套简式。源图本来等比时保持等比，不能以额外的 X/Y 拉伸掩盖定位误差。

## 附带审计工具

脚本仅依赖 Python 标准库：

```text
python <skill>/scripts/pptx_audit.py inspect <input.pptx> --out <inventory.json>
python <skill>/scripts/pptx_audit.py inspect <input.pptx> --out <inventory.json> --extract-media <new-empty-directory>
python <skill>/scripts/pptx_audit.py compare-text <stage1.pptx> <stage2.pptx> --name-prefix TEXT_ --out <text-regression.json>
```

`inspect` 读取实际 slide 顺序、画布、原生对象、图片资源/裁剪/变换及祖先组变换，统计实心填色、描边和形状节点。它不渲染、不 OCR、不判断图层好坏。媒体仅提取到新目录，只导出 ZIP 的 `ppt/media` 文件，不跟随外链。

`compare-text` 按 slide 顺序和 shape ID（或稳定唯一名称）对比含文字的原生形状，记录内容、格式、结构化哈希和祖先组变换。它拒绝空基线并以非零状态报告缺失、变化或新增对象。宿主字体替换、主题和布局继承变化仍须实际渲染检查。

辅助脚本不是完整保真验证器。最终报告还应绑定交付 PPTX 的 SHA-256，分别记录内容/拓扑、视觉、实际编辑结果与未解决事项。修改后重新渲染受影响页，保证预览来自实际交付版本。

## 运行与交付

通过当前工具清单和 `load_workspace_dependencies` 等宿主接口定位库。不要复制本例的绝对 Node、Python、字体路径或版本目录。作者脚本按当前图生成；本 skill 不假装提供适用于任意科研图的全自动一键描摹器。

Windows 用 PowerPoint COM 核对时，一段会话打开任务副本、导出所需页、检查对象，再仅关闭该副本。不要全局 Quit、杀进程或关闭用户文件。离线任务无需额外制造 live 会话；用户明确要求观看绘制时，用可用的受支持 live 工作流。

最终文件用新名称，保留两阶段 PPTX/PNG。清单、源图、脚本和 QA 留在工作区，不把临时素材全部交付，也不把实现细节写进科研图。
