---
name: usage-resolver
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。作为"解决者"角色，检测问题解决信号，计算耗费时间，调用 usage-recorder 完成数据存储。此 skill 设计为在 UserPromptSubmit hook 中自动调用，与 usage-observer 配合工作。
metadata:
  version: "2.1.0"
  author: "Claude"
  role: "resolver"
  system: "claude-usage-analytics"
  trigger_type: "resolution_detection"
---

# Usage Resolver - 问题解决者

## Overview

本 Skill 的职责由 **keyword_router.py (UserPromptSubmit hook)** 和 **stop_recorder.py (Stop hook)** 共同完成：

### keyword_router.py (UserPromptSubmit hook)
1. 检测用户输入中的**解决信号关键词**
2. 标记 `tracking_state.json` 中的问题为 `resolved`
3. 记录 `end_time` 并计算 `elapsed_minutes`
4. 将问题从 `active_problems` 移动到 `resolved_problems`

### stop_recorder.py (Stop hook)
1. 处理 `resolved_problems` 列表，写入日期 md 文件
2. 处理 `active_problems` 列表（检查 transcript 中的解决信号）
3. 清空已处理的问题列表

**无需手动触发此 skill**，所有解决检测和记录均由 hooks 自动完成。

---

## 解决信号关键词

keyword_router.py 检测以下关键词判断问题是否已解决：

| 中文 | 英文 |
|------|------|
| 好了 | done |
| 解决了 | fixed |
| 成功了 | works |
| 可以了 | solved |
| 没问题了 | working now |
| 修好了 | resolved |
| 搞定了 | it works |
| 完成了 | thanks |
| 弄好了 | - |
| 谢谢 | - |

---

## 数据格式

Stop hook 写入的记录采用统一 9 列格式：

```
| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |
```

---

## tracking_state.json 结构

```json
{
  "active_problems": [
    {
      "id": "p_20260316_143000",
      "session_id": "session_abc",
      "problem": "问题描述...",
      "start_time": "2026-03-16T14:30:00",
      "status": "active"
    }
  ],
  "resolved_problems": [
    {
      "id": "p_20260316_143000",
      "session_id": "session_abc",
      "problem": "问题描述...",
      "start_time": "2026-03-16T14:30:00",
      "end_time": "2026-03-16T14:35:00",
      "elapsed_minutes": 5.0,
      "status": "resolved"
    }
  ]
}
```

---

## 存储位置

数据存储在用户主目录：
- Windows: `%USERPROFILE%\.claude\claude-analysis\YYYY-MM-DD.md`
- Mac/Linux: `~/.claude/claude-analysis/YYYY-MM-DD.md`

状态文件：`~/.claude/claude-analysis/tracking_state.json`
