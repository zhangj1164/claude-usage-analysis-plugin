# Claude Usage Analysis Plugin

## 安装方法

### 方法 1: 通过 Claude Code CLI 安装（推荐）

```bash
# 从 GitHub 安装最新版本
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin

# 或安装特定版本
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin@v1.0.0
```

### 方法 2: 本地安装

```bash
# 1. 克隆仓库
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git

# 2. 进入目录并安装
cd claude-usage-analysis-plugin
claude plugin install .
```

### 方法 3: 通过设置文件配置

在项目的 `.claude/CLAUDE.md` 或用户目录的 `~/.claude/CLAUDE.md` 中添加：

```markdown
## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin
```

## 使用说明

安装完成后，插件会自动通过 `UserPromptSubmit` Hook 工作：

1. **自动检测**: 当您在会话中提到"错误"、"问题"、"报错"等关键词时，usage-observer 会自动分析并记录
2. **数据存储**: 记录存储在 `~/.claude/claude-analysis/YYYY-MM-DD.md`
3. **手动记录**: 也可以直接说"记录这个问题"手动触发 usage-recorder

## 验证安装

```bash
# 查看已安装的插件
claude plugin list

# 应该能看到 claude-usage-analysis-plugin 及其 skills
```

## 卸载

```bash
claude plugin remove claude-usage-analysis-plugin
```
