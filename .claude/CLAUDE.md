# Claude Usage Analysis Plugin Configuration

## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin

## Instructions

当用户遇到问题时，自动采集使用数据：

1. **自动检测**: 当用户提到"错误"、"问题"、"报错"、"失败"等关键词时，usage-observer 会自动触发
2. **分析会话**: 提取问题描述、会话阶段、问题类型、相关文档等信息
3. **询问补充**: 向用户确认耗费时间和解决状态
4. **记录数据**: 调用 usage-recorder 将数据存储到本地 markdown 文件

数据存储位置: `~/.claude/claude-analysis/YYYY-MM-DD.md`
