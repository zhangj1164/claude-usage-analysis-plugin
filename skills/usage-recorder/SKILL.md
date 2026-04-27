---
name: usage-recorder
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。确认问题已记录归档，配合 stop_recorder.py 完成数据写入。此 skill 由 UserPromptSubmit hook 自动调用，无需用户手动触发。
metadata:
  version: "2.1.0"
  author: "Claude"
  role: "recorder"
  system: "claude-usage-analytics"
  trigger_type: "automatic"
---

# Usage Recorder - 使用记录器

## Overview

本 Skill 是 **usage-analytics 自动追踪系统**的记录确认组件。

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
    ├─ 用 Read 工具确认问题已归档
    └─ 静默完成
    ↓
Stop Hook (stop_recorder.py)
    └─ 自动将已解决问题写入日期 md 文件
```

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

**当此 skill 被 hook 自动触发时，执行以下步骤：**

### Step 1: 确认归档状态

使用 **Read 工具**读取 `~/.claude/claude-analysis/tracking_state.json`，检查 `resolved_problems` 列表中是否有本次会话的记录。

**如果文件不存在**：静默完成，不报错——hook 可能尚未写入。
**如果列表为空**：静默完成，本次触发可能为误判。

### Step 2: 静默完成

确认问题状态后，**不向用户显示任何消息**，避免打断工作流程。

Stop hook 会在 Claude 回复完成后自动将问题写入日期 md 文件。

---

## 边界条件

| 场景 | 处理 |
|------|------|
| tracking_state.json 不存在 | 静默完成，不报错 |
| resolved_problems 为空 | 静默完成，可能误触发 |
| JSON 解析失败 | 静默完成，不尝试修复 |
| 与 resolver 同时触发 | 两者各自独立确认，不冲突 |

---

## 数据格式

Stop hook 写入的记录采用统一 9 列格式：

```
| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |
```

---

## 与 resolver 的分工

- **usage-recorder (本skill)**: 侧重"确认记录已完成"，纯静默
- **usage-resolver**: 侧重"确认归档 + 可选耗时通知"，有条件地反馈

tracking_state.json 结构定义见 usage-resolver。

---

## 存储位置

- 数据文件: `~/.claude/claude-analysis/YYYY-MM-DD.md`
- 状态文件: `~/.claude/claude-analysis/tracking_state.json`
