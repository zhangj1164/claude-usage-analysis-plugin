---
name: usage-resolver
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。作为"解决者"角色，检测问题解决信号，计算耗费时间，调用 usage-recorder 完成数据存储。此 skill 设计为在 UserPromptSubmit hook 中自动调用，与 usage-observer 配合工作。
metadata:
  version: "2.0.0"
  author: "Claude"
  role: "resolver"
  system: "claude-usage-analytics"
  trigger_type: "resolution_detection"
---

# Usage Resolver - 问题解决者

## Overview

本 Skill 的职责已由 **Stop hook (stop_recorder.py)** 自动处理。当 Claude 完成回复时，Stop hook 会：

1. 检查 `tracking_state.json` 中的活动问题
2. 读取 transcript 判断是否包含解决信号
3. 计算耗时并写入日期 md 文件
4. 已解决的问题从活动列表中移除

**无需手动触发此 skill**，所有解决检测和记录均由 Stop hook 自动完成。

---

## 解决信号关键词

Stop hook 检测以下关键词判断问题是否已解决：

| 中文 | 英文 |
|------|------|
| 好了 | done |
| 解决了 | fixed |
| 成功了 | works |
| 可以了 | solved |
| 没问题了 | working now |
| 修好了 | resolved |
| 搞定了 | it works |
| 完成了 | - |
| 弄好了 | - |

---

## 数据格式

Stop hook 写入的记录采用统一 9 列格式：

```
| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |
```

---

## 存储位置

数据存储在用户主目录：
- Windows: `%USERPROFILE%\.claude\claude-analysis\YYYY-MM-DD.md`
- Mac/Linux: `~/.claude/claude-analysis/YYYY-MM-DD.md`

状态文件：`~/.claude/claude-analysis/tracking_state.json`
