---
name: usage-observer
description: 当用户在 Claude Code 会话中提到错误、失败、问题、报错、error、exception、bug、不对、错了、有问题等关键词时自动触发。此 skill 由 UserPromptSubmit hook 自动调用，无需用户手动触发。
metadata:
  version: "4.0.0"
  author: "Claude"
  role: "observer"
  system: "claude-usage-analytics"
  trigger_type: "automatic"
---

# Usage Observer - 使用观察者

## Overview

本 Skill 是 **usage-analytics 自动追踪系统**的核心组件。当 UserPromptSubmit hook (keyword_router.py) 检测到问题关键词时，会通过 additionalContext 自动触发本 skill。

**自动触发流程：**
```
用户输入包含问题关键词
    ↓
UserPromptSubmit Hook (keyword_router.py)
    ├─ 创建 tracking_state.json 追踪记录
    └─ additionalContext 强制调用本 skill
    ↓
usage-observer skill（当前）
    ├─ 从上下文提取问题描述、阶段、类型
    └─ 静默完成，不干扰用户对话
    ↓
Stop Hook (stop_recorder.py)
    └─ Claude 回复完成后自动记录到日期 md 文件
```

**职责分工：**
- **keyword_router.py**: 检测关键词，创建追踪记录，触发本 skill
- **usage-observer (本 skill)**: 观察问题上下文，静默完成
- **stop_recorder.py**: 自动记录到日期文件

---

## 执行指令

**当此 skill 被 hook 自动触发时，立即执行以下步骤：**

### Step 1: 分析问题内容

从用户输入和会话上下文中提取：
1. **问题描述**: 从用户当前提问中提取核心问题
2. **会话阶段**: 根据关键词推断（需求分析/代码编写/调试/测试/部署）
3. **问题类型**: 自动分类（工具错误/理解偏差/执行失败/性能问题/其他）
4. **相关文档**: 提取提及的文件路径（如有）

### Step 2: 确认追踪记录

确认 `~/.claude/claude-analysis/tracking_state.json` 中已有追踪记录（由 keyword_router.py 创建）。

### Step 3: 静默完成

**不要向用户显示任何消息**，避免打断工作流程。Stop hook 会在 Claude 回复完成后自动记录。

---

## 阶段识别规则

从对话内容自动推断会话阶段：

| 关键词 | 推断阶段 |
|--------|----------|
| 需求、设计、规划、分析、结构 | 需求分析 |
| 创建、编写、实现、开发、写代码 | 代码编写 |
| 调试、排查、修复、bug、错误 | 调试 |
| 测试、验证、断言、用例 | 测试 |
| 部署、发布、上线、构建、打包 | 部署 |

## 问题类型分类规则

| 类型 | 说明 | 关键词 |
|------|------|--------|
| 工具错误 | 工具使用不当或工具本身问题 | skill 未触发、命令参数错误、工具失败 |
| 理解偏差 | 理解需求或上下文有误 | 误解意图、理解错误、上下文不对 |
| 执行失败 | 执行过程中出错 | 测试失败、构建失败、命令超时、报错 |
| 性能问题 | 响应慢或资源占用高 | 响应慢、内存不足、超时 |
| 其他 | 不属于以上类别 | 文档不清晰、依赖缺失 |

---

## 注意事项

1. **自动触发**: 由 hook 通过 additionalContext 自动调用，无需用户手动触发
2. **静默执行**: 不向用户显示任何消息，完全后台运行
3. **不直接记录数据**: 数据记录由 Stop hook 自动完成
4. **状态持久化**: 使用 `tracking_state.json` 跨 Hook 调用共享状态