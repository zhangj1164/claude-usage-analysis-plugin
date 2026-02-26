# Claude Usage Analysis Plugin

## 安装方法

### 方法 1: 通过 Claude Code CLI 安装（推荐）

**步骤 1**: 添加 Marketplace 源
```bash
claude plugin marketplace add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

**步骤 2**: 安装插件（插件名为 `usage-analytics`）
```bash
claude plugin install usage-analytics
# 或简写
claude plugin i usage-analytics
```

### 方法 2: 本地安装

```bash
# 1. 克隆仓库
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git

# 2. 进入目录，添加本地 marketplace 并安装
cd claude-usage-analysis-plugin
claude plugin marketplace add .
claude plugin install usage-analytics
```

## 使用说明

安装完成后，插件会自动通过 `UserPromptSubmit` Hook 工作：

1. **自动检测**: 当您在会话中提到"错误"、"问题"、"报错"等关键词时，usage-observer 会自动分析并记录
2. **数据存储**: 记录存储在 `~/.claude/claude-analysis/YYYY-MM-DD.md`
3. **手动记录**: 也可以直接说"记录这个问题"手动触发 usage-recorder

## 验证安装

```bash
# 查看已配置的 marketplace
claude plugin marketplace list

# 查看已安装的插件
cat ~/.claude/plugins/installed_plugins.json
```

## 卸载

```bash
claude plugin uninstall usage-analytics
# 或
claude plugin remove usage-analytics
```
