---
name: usage-resolver
description: 当用户在 Claude Code 会话中提到解决信号关键词（如"好了"、"解决了"、"谢谢"、"done"、"fixed"等）时自动触发。作为"解决者"角色，检测问题解决信号，计算耗费时间，调用 usage-recorder 完成数据存储。此 skill 设计为在 UserPromptSubmit hook 中自动调用，与 usage-observer 配合工作。
metadata:
  version: "1.0.0"
  author: "Claude"
  role: "resolver"
  system: "claude-usage-analytics"
  trigger_type: "resolution_detection"
---

# Usage Resolver - 问题解决者

## Overview

本 Skill 用于**自动检测问题解决信号**，计算问题解决耗费时间，并完成数据记录。当用户提到"好了"、"解决了"、"谢谢"等关键词时，本 skill 会查找当前会话的活动问题，计算耗时，调用 `usage-recorder` 完成存储。

**职责分工：**
- **usage-observer (观察者)**: 检测问题，创建追踪记录
- **usage-resolver (解决者)**: 检测解决信号，计算耗时，完成存储
- **usage-recorder (记录员)**: 接收数据，写入文件

数据最终存储在用户目录的 `.claude/claude-analysis/` 下。

---

## 执行指令

**当此 skill 被触发时，必须执行以下步骤：**

### Step 1: 查找活动问题

调用 auto_resolver.py 脚本查找并解决问题：

```bash
python scripts/auto_resolver.py \
  --user-input "[用户输入]" \
  --session-id "[会话ID]"
```

或使用 Python 直接调用：

```python
from scripts.auto_resolver import resolve_and_record

result = resolve_and_record(
    session_id=params["session_id"],
    user_input=params["user_input"]
)
```

脚本会自动：
1. 查找当前会话的活动问题
2. 计算从问题开始到解决的耗时
3. 调用 usage-recorder 完成数据存储

### Step 2: 静默完成

**不要向用户显示确认消息**，避免打断工作流程。

---

## 解决信号关键词

| 中文 | 英文 |
|------|------|
| 好了 | done |
| 解决了 | fixed |
| 成功了 | works |
| 谢谢 | thanks |
| 可以了 | solved |
| 修好了 | working now |
| 搞定了 | resolved |
| 完成了 | it works |
| 弄好了 | perfect |
| 没问题了 | - |

---

## 注意事项

1. **静默执行**: 不向用户显示任何消息
2. **查找最新问题**: 如果有多个活动问题，取最新的一个
3. **自动计算耗时**: 从问题创建时间到解决时间
4. **调用 recorder**: 完成数据存储
5. **清理状态**: 从活动问题列表移除已解决的问题

---

## 存储位置

数据存储在用户主目录：
- Windows: `%USERPROFILE%\.claude\claude-analysis\YYYY-MM-DD.md`
- Mac/Linux: `~/.claude/claude-analysis/YYYY-MM-DD.md`

状态文件：`~/.claude/claude-analysis/tracking_state.json`