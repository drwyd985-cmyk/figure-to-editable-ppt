# 上传到 GitHub

本发布包只准备本地文件，没有创建远程仓库、推送提交或发布 Release。推荐仓库名为 `figure-to-editable-ppt`。

## 上传前

1. 本包已按维护者选择添加 MIT 许可证，版权署名为 `Copyright (c) 2026 drwyd985-cmyk`。上传时保留根目录及技能子目录中的 `LICENSE`。
2. README 安装示例已使用 `drwyd985-cmyk`。若改用其他账户、仓库名或默认分支，同步更新安装链接。
3. 核对 README 中的运行条件。目标环境需要可用的 `presentations` 技能、PPT 生成运行库和实际渲染能力。

## 网页上传

1. 在 GitHub 新建仓库，填写名称与描述，按分享范围选择 Public 或 Private。
2. 解压 `figure-to-editable-ppt-github.zip`，打开其中的 `figure-to-editable-ppt` 文件夹。
3. 在仓库页面选择 **Add file → Upload files**；空仓库也可以使用页面中的上传已有文件入口。
4. 上传该文件夹内的 `README.md`、`LICENSE`、`.gitignore`、`.gitattributes`、`docs/` 和 `skills/`。保持内部目录结构。
5. 提交文件后，检查仓库首页显示 README，且技能入口位于 `skills/figure-to-editable-ppt/SKILL.md`。

如果只把 ZIP 作为一个文件上传到仓库，安装示例中的技能目录链接不会成立。ZIP 用于传输和解压；仓库里应呈现解压后的文件。检查资源管理器是否显示以点开头的配置文件，避免漏掉 `.gitignore` 和 `.gitattributes`。

网页上传不会应用 Git 的 `.gitattributes` 转换；后续用 Git 维护仓库时，该文件会统一 Markdown、Python 和 YAML 文本换行。详细步骤见 [GitHub 官方上传说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。

## 上传后验证

- 打开 `skills/figure-to-editable-ppt/SKILL.md`，确认三个参考文档及脚本的相对链接可访问。
- 使用 README 中的实际仓库链接，在另一套测试环境中安装技能；避免覆盖自己正在使用的版本。
- 检查安装环境是否具备 README 列出的生成与渲染依赖。选用可以公开的测试图，核对两阶段交付和实际编辑效果。
- 若希望固定一个可复现版本，可在完成安装验证后创建版本标签或 Release。

当前包没有包含论文图、患者数据、案例 PPTX 或重建截图。今后添加演示素材时，单独确认素材的公开范围与许可。

## 本地包的检查范围

首次打包已检查技能 frontmatter、YAML 元数据、内部文档链接和文件清单，并在隔离目录验证审计脚本的成功与差异报告行为。本次许可更新另行检查两个许可证的一致性、署名、文档链接和 ZIP 内容；原有指令与脚本保持不变。检查记录放在发布包外，避免把本机路径和测试临时文件上传到仓库。

这些检查验证技能结构与辅助脚本，不代表已在所有平台完成图形重建，也不代替发布后的全新安装验证。
