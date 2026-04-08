---
name: usage-recorder
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。此 skill 由 UserPromptSubmit hook 自动调用，无需用户手动触发。
metadata:
  version: "2.0.0"
  author: "Claude"
  role: "recorder"
  system: "claude-usage-analytics"
  trigger_type: "automatic"
---

# Usage Recorder - 使用记录器

## Overview

本 Skill 是 **usage-analytics 自动追踪系统**的记录组件。当 UserPromptSubmit hook (keyword_router.py) 检测到解决信号关键词时，会通过 additionalContext 自动触发本 skill。

**自动触发流程：**
```
用户输入包含解决信号
    ↓
UserPromptSubmit Hook (keyword_router.py)
    ├─ 标记 tracking_state.json 中的问题为 resolved
    ├─ 计算 elapsed_minutes
    └─ additionalContext 强制调用本 skill
    ↓
usage-recorder skill（当前）
    ├─ 确认问题已归档
    └─ 静默完成，不干扰用户对话
    ↓
Stop Hook (stop_recorder.py)
    └─ 自动将已解决问题写入日期 md 文件
```

**职责分工：**
- **keyword_router.py**: 检测解决信号，标记问题状态，触发本 skill
- **usage-recorder (本 skill)**: 确认记录完成，静默执行
- **stop_recorder.py**: 自动写入日期文件

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

## 执行指令

**当此 skill 被 hook 自动触发时，立即执行以下步骤：**

### Step 1: 确认问题状态

检查 `~/.claude/claude-analysis/tracking_state.json` 中的 `resolved_problems` 列表，确认问题已正确归档。

### Step 2: 静默完成

**不要向用户显示任何消息**，避免打断工作流程。Stop hook 会在 Claude 回复完成后自动将问题写入日期 md 文件。

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
  "active_problems": [],
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

## 注意事项

1. **自动触发**: 由 hook 通过 additionalContext 自动调用，无需用户手动触发
2. **静默执行**: 不向用户显示任何消息，完全后台运行
3. **数据写入由 Stop hook 完成**: 本 skill 只确认状态，不直接写文件
4. **状态持久化**: 使用 `tracking_state.json` 跨 Hook 调用共享状态

---

## 存储位置

数据存储在用户主目录：
- Windows: `%USERPROFILE%\.claude\claude-analysis\YYYY-MM-DD.md`
- Mac/Linux: `~/.claude/claude-analysis/YYYY-MM-DD.md`

状态文件：`~/.claude/claude-analysis/tracking_state.json`