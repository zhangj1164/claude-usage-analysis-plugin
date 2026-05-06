---
name: usage-observer
description: 当用户在 Claude Code 会话中提到错误、失败、问题、报错、error、exception、bug、不对、错了、有问题等关键词时自动触发。此 skill 由 UserPromptSubmit hook 和 SessionStart hook 自动调用，无需用户手动触发。
metadata:
  version: "4.2.0"
  author: "Claude"
  role: "observer"
  system: "claude-usage-analytics"
  trigger_type: "automatic"
---

# Usage Observer - 使用观察者

## Overview

本 Skill 是 **usage-analytics 自动追踪系统**的核心触发组件。

**自动触发流程：**
```
用户输入包含问题关键词 OR 会话从 summary 继续
    ↓
UserPromptSubmit Hook (keyword_router.py) OR SessionStart Hook (session_resumer.py)
    ├─ 创建 tracking_state.json 追踪记录
    │  ├─ 阶段: 从对话内容推断（见下方分类表）
    │  ├─ 类型: 从关键词推断（见下方分类表）
    │  └─ status: "active"
    └─ additionalContext 强制调用本 skill
    ↓
usage-observer skill（当前）
    └─ 静默完成，不干扰用户对话
    ↓
Stop Hook (stop_recorder.py)
    └─ Claude 回复完成后自动记录到日期 md 文件
```

---

## 执行指令

**当此 skill 被 hook 自动触发时，立即静默完成：**

此 skill 由 Hook 通过 additionalContext 触发，**不执行任何操作**。所有工作已由 Hook 完成：
- `keyword_router.py` 已创建追踪记录（含阶段和类型分类）
- `stop_recorder.py` 将在会话结束时记录

**不要执行任何工具调用**（Read/Bash/Grep 等），避免触发权限提示。

---

## 阶段识别规则

keyword_router.py 从对话内容自动推断会话阶段：

| 关键词 | 推断阶段 |
|--------|----------|
| 需求、设计、规划、分析、结构 | 需求分析 |
| 创建、编写、实现、开发、写代码 | 代码编写 |
| 调试、排查、修复、bug、错误 | 调试 |
| 测试、验证、断言、用例 | 测试 |
| 部署、发布、上线、构建、打包 | 部署 |

## 问题类型分类规则

keyword_router.py 从关键词推断问题类型：

| 类型 | 说明 | 关键词 |
|------|------|--------|
| 工具错误 | 工具使用不当或工具本身问题 | skill 未触发、命令参数错误、工具失败 |
| 理解偏差 | 理解需求或上下文有误 | 误解意图、理解错误、上下文不对 |
| 执行失败 | 执行过程中出错 | 测试失败、构建失败、命令超时、报错 |
| 性能问题 | 响应慢或资源占用高 | 响应慢、内存不足、超时 |
| 其他 | 不属于以上类别 | 文档不清晰、依赖缺失 |

> 以上规则供参考理解系统行为，本 skill 不直接执行分类。

---

## 边界条件

| 场景 | 处理 |
|------|------|
| tracking_state.json 已存在 | Hook 会追加新问题到 active_problems |
| 同一会话多次触发 | 每次触发创建独立问题条目 |
| 会话继续(summary恢复) | SessionStart hook 恢复未解决问题 |
| 误触发(非问题关键词) | Hook 已有容错，本 skill 静默完成 |

---

## 与系统其他角色的协作

```
usage-observer（本skill）→ 触发追踪
        ↓
usage-resolver → 确认归档 + 可选通知
usage-recorder → 确认记录
        ↓
stop_recorder.py → 写入日期文件
        ↓
usage-analyst → 生成洞察
usage-coach → 改进建议
```

---

## 存储位置

- 状态文件: `~/.claude/claude-analysis/tracking_state.json`
- 数据文件: `~/.claude/claude-analysis/YYYY-MM-DD.md`
