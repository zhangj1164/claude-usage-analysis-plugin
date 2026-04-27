---
name: usage-resolver
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。配合 keyword_router.py 确认问题已归档，可选通知用户解决耗时。此 skill 由 UserPromptSubmit hook 自动调用，无需用户手动触发。
metadata:
  version: "2.2.0"
  author: "Claude"
  role: "resolver"
  system: "claude-usage-analytics"
  trigger_type: "automatic"
---

# Usage Resolver - 问题解决确认

## Overview

本 Skill 与 **usage-recorder** 配合工作，职责分工：

| 角色 | 触发时机 | 职责 |
|------|----------|------|
| keyword_router.py | UserPromptSubmit | 检测解决信号，更新 tracking_state.json |
| **usage-resolver (本skill)** | keyword_router 触发后 | 确认归档状态，可选通知耗时 |
| stop_recorder.py | Stop hook | 将已解决问题写入日期 md 文件 |
| usage-recorder | keyword_router 触发后 | 确认记录完成，静默执行 |

---

## 执行指令

**当此 skill 被 hook 自动触发时，执行以下步骤：**

### Step 1: 验证归档状态

读取 `~/.claude/claude-analysis/tracking_state.json`，检查 `resolved_problems` 列表中是否有本次会话的记录。

**如果文件不存在或列表为空**：不报错，静默完成——hook 可能尚未写入。

### Step 2: 可选耗时通知

如果 `resolved_problems` 中存在当前问题的记录且 `elapsed_minutes > 10`，可在回复中简短附注：

```
（本次问题耗时约 X 分钟，已记录）
```

**如果耗时 ≤ 10 分钟**：不通知，避免打断用户节奏。

### Step 3: 静默完成

不向用户显示多余消息。Stop hook 会自动写入日期 md 文件。

---

## 边界条件

| 场景 | 处理 |
|------|------|
| tracking_state.json 不存在 | 静默完成，不报错 |
| resolved_problems 为空 | 静默完成，可能 hook 尚未处理 |
| 多个问题同时解决 | 只通知最近一个的耗时 |
| 非问题会话误触发 | 静默完成，不影响对话 |

---

## 与 recorder 的区别

- **usage-recorder**: 侧重"记录已完成"，纯静默
- **usage-resolver (本skill)**: 侧重"确认归档+可选通知"，有条件地反馈耗时

解决信号关键词和数据格式定义在 usage-recorder 中，本 skill 不重复定义。

---

## 存储位置

- 数据文件: `~/.claude/claude-analysis/YYYY-MM-DD.md`
- 状态文件: `~/.claude/claude-analysis/tracking_state.json`
