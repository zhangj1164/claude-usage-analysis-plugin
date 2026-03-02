# Claude Usage Analysis Plugin Configuration

## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin

## Instructions

### 工作风格（Proactive Mode）

**主动推进任务，减少来回确认：**

- 当用户提出需求时，先完整理解目标，然后**主动规划并执行**完整方案
- 遇到不确定的问题时，基于最佳实践做出合理决策，而不是每一步都询问
- 执行多个相关步骤后，再统一汇报结果和关键决策点
- 如果任务涉及多个文件修改，一次性完成后再提交

**例外情况（才需要询问）：**
- 涉及删除数据、强制推送、破坏性操作
- 用户明确要求 "先问我" 或 "逐步确认"
- 存在多个互斥方案且优劣不明显

### 自动采集使用数据

当用户遇到问题时，自动采集使用数据：

1. **自动检测**: 当用户提到"错误"、"问题"、"报错"、"失败"等关键词时，usage-observer 会自动触发
2. **分析会话**: 提取问题描述、会话阶段、问题类型、相关文档等信息
3. **询问补充**: 向用户确认耗费时间和解决状态
4. **记录数据**: 调用 usage-recorder 将数据存储到本地 markdown 文件

数据存储位置: `~/.claude/claude-analysis/YYYY-MM-DD.md`
