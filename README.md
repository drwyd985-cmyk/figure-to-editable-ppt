# figure-to-editable-ppt

免费提供、采用 [MIT License](LICENSE) 的 Codex 技能，将科研示意图、机制图或 PPTX 内的整张位图分两阶段重建为可编辑 PowerPoint。

**Figure to Editable PPT** is a free Codex skill that rebuilds scientific figures as editable PowerPoint slides in two stages. It first exports a version with editable text for your review, then reconstructs the underlying graphics after your confirmation. The workflow preserves approved text—including its content, formatting, and position—rebuilds complete, continuous organ base shapes, and consolidates fragmented light and dark layers of the same line into coherent editable paths. It also checks for duplicate contours, missing details, and practical editability through actual editing tests. To complete both stages without interruption, add: **“Complete the entire workflow continuously, without pausing for intermediate confirmation.”**

本仓库提供技能指令、参考文档和只读审计脚本。图形重建由具备图像理解、文件操作和 PPT 原生对象生成能力的代理执行；没有针对任意图片的独立一键转换程序。

## 能做什么

- **第一阶段：文字可编辑。** 核对原图文字，恢复原生文字框及混合格式，保留底层图像，导出 PPTX 和实际渲染预览。
- **第二阶段：图形可编辑。** 保留第一阶段文字，按完整组织底形、独立路线、细胞和细胞核重建原生形状，按区域与语义分组。
- **修复已有重建结果。** 处理过度描摹产生的明暗碎层、粗线、拼缝和不完整底形。
- **分别核查内容、视觉与编辑体验。** 检查箭头和连接关系，比较实际渲染，并抽查修改文字、移动器官、修改线宽和选择细胞。

适用于忠实重建已有图片或 PPTX 中的整图位图，也会检查并保留已有合格的原生对象。论文生成新演示文稿、普通统计作图不属于本技能的用途。

## 工作方式与交付

默认先交付文字版供用户核对，再进入图形重建。如果用户明确要求“全流程连续完成，无需中途确认”，则保存第一阶段快照后直接完成第二阶段。

通常交付四个独立文件，具体名称随任务确定：

| 文件 | 内容 |
| --- | --- |
| 阶段1_文字可编辑.pptx | 底层图像及可编辑文字 |
| 阶段1_预览.png | 来自阶段1 PPTX 的实际渲染 |
| 阶段2_图文可编辑.pptx | 原生文字与按语义组织的可编辑图形 |
| 阶段2_预览.png | 来自阶段2 PPTX 的实际渲染 |

原文件保留不变。字体、轮廓、阴影和复杂纹理可能需要拟合；结果应说明替代和残留问题，不承诺像素级一致。复杂图可能需要较长时间和多轮局部校准。

## 运行条件

| 条件 | 用途与范围 |
| --- | --- |
| 支持 Agent Skills 的代理环境 | 读取 `SKILL.md`，理解图片，运行脚本并操作任务文件；本技能主要面向 Codex |
| 可用的 `presentations` 技能及其运行库 | 当前技能指令依赖它完成 PPT 原生对象生成和导出验证；本仓库不包含该技能或其运行库 |
| PPT 渲染工具 | 用于检查实际导出效果；本地验证环境为 Windows + Microsoft PowerPoint |
| Python 3 | 运行附带的 `pptx_audit.py`；脚本只用标准库，无额外 `pip` 依赖 |
| 可用字体 | 匹配原图文字；缺失字体时应记录替代并重新渲染 |

OCR 可作为文字候选来源，但仍需视觉核对。没有本机 PowerPoint 时，可按技能指令使用宿主可用的渲染器，并说明兼容性与编辑验证的范围；本发布包未完成 macOS、Linux 或其他代理宿主的端到端验证。

安装本技能不会安装 Microsoft Office、`presentations` 或其依赖。若目标环境缺少这些能力，应先补齐环境，再运行重建；独立审计脚本仍可在 Python 环境下使用。依赖由目标宿主动态定位，仓库不固定本机缓存路径或版本目录。

## 安装

### 使用 Codex Skill Installer

以下安装链接按 GitHub 用户名 `drwyd985-cmyk`、仓库名 `figure-to-editable-ppt` 和默认分支 `main` 配置，待仓库上传后使用。如果发布到其他账户，或修改仓库名、默认分支，需相应调整链接。在 Codex 中输入：

```text
$skill-installer 请安装这个技能：
https://github.com/drwyd985-cmyk/figure-to-editable-ppt/tree/main/skills/figure-to-editable-ppt
```

这里安装的是 `skills/figure-to-editable-ppt` 子目录。安装器会按当前宿主设置选择安装位置；如果已有同名技能，先核对现有版本，再决定如何更新。

### 手动安装到一个项目

将仓库中的 `skills/figure-to-editable-ppt` 文件夹复制到目标项目的 `.agents/skills/` 下：

```text
your-project/
└── .agents/
    └── skills/
        └── figure-to-editable-ppt/
            ├── SKILL.md
            ├── agents/
            ├── references/
            └── scripts/
```

在该项目中使用 Codex。若技能没有出现，可重启后再检查。技能目录必须保留其内部相对路径，不能只复制 `SKILL.md`。

当前安装和项目目录约定见 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)。该文档还介绍了后续将技能打包为插件的分发方式；本仓库当前提供直接技能目录。

## 使用示例

向代理提供原图或 PPTX 文件后，选择以下任一方式。

**连续完成两个阶段：**

```text
使用 $figure-to-editable-ppt 处理附带的科研图。
先导出文字可编辑版和实际渲染预览，再重建底层图形。
全流程连续完成，无需中途确认。保留原文件。
```

**先核对文字再继续：**

```text
使用 $figure-to-editable-ppt 处理这张图。
先完成文字可编辑版并导出预览，等我核对后再重建底层图形。
```

**只检查已有两阶段文件：**

```text
使用 $figure-to-editable-ppt 核对这两个 PPTX 的文字是否保留一致。
本次只做检查，不重绘、不改文件，报告检查范围和差异。
```

原图中的标签属于待重建内容，不作为代理的操作指令；没有明确校订要求时，保留原图术语和拼写，并单独记录疑点。

## 独立使用审计脚本

以下命令在仓库根目录执行。把示例文件名替换为实际 PPTX 路径；如环境使用 `python3`，相应替换命令。

读取画布、原生对象、文字、图片关系与变换：

```shell
python skills/figure-to-editable-ppt/scripts/pptx_audit.py inspect input.pptx --out work/inventory.json
```

同时提取嵌入媒体，目标目录必须尚不存在：

```shell
python skills/figure-to-editable-ppt/scripts/pptx_audit.py inspect input.pptx --out work/inventory.json --extract-media work/source-media
```

比较两阶段的原生文字对象：

```shell
python skills/figure-to-editable-ppt/scripts/pptx_audit.py compare-text stage1.pptx stage2.pptx --name-prefix TEXT_ --out work/text-regression.json
```

默认按幻灯片顺序与形状 ID 匹配。若 ID 合理变化而名称稳定且唯一，可加 `--match-by name`；省略 `--name-prefix` 会检查所有含文字的原生对象。

退出码：`0` 表示命令成功且文字比较通过，`1` 表示比较发现差异，`2` 表示输入、参数或处理错误。没有匹配文字的空基线会被拒绝。

脚本不执行 OCR，不渲染图片，也不判断图形保真度。文字回归检查覆盖原生文字节点与祖先变换；主题、布局继承、字体替换、连接拓扑和实际编辑体验仍需另行检查。

## 仓库结构

```text
figure-to-editable-ppt/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── docs/
│   └── github-publish.md
└── skills/
    └── figure-to-editable-ppt/
        ├── SKILL.md
        ├── LICENSE
        ├── agents/openai.yaml
        ├── references/
        │   ├── stage1-text.md
        │   ├── stage2-geometry.md
        │   └── state-and-coordinates.md
        └── scripts/pptx_audit.py
```

技能入口见 [SKILL.md](skills/figure-to-editable-ppt/SKILL.md)。本包保留原有技能指令、参考文档与脚本，新增仓库使用说明和许可证；不附科研输入图、重建输出、宿主缓存或账户配置。

## 发布与许可证

本地目录已按 GitHub 仓库结构整理，上传步骤见 [GitHub 发布说明](docs/github-publish.md)。

本项目采用 [MIT License](LICENSE)，版权署名为 **Copyright (c) 2026 drwyd985-cmyk**。允许免费使用、修改、分发和商用；复制或分发软件的副本或实质部分时，须保留版权声明与许可声明。完整条款以许可证文件为准。

Licensed under the MIT License. Free to use, modify, and redistribute, including for commercial purposes. Retain the copyright and license notices in copies or substantial portions of the software.

仓库根目录与可安装的技能子目录均包含相同的 `LICENSE`，便于单独安装或分享技能时保留许可声明。外部依赖遵循各自的许可；本技能免费提供，不包含模型服务、Microsoft Office 或其他依赖可能产生的费用。
