---
name: usage-observer
description: 当用户在 Claude Code 会话中提到错误、失败、问题、报错、error、exception、bug、失败、不对、错了、有问题等关键词时自动触发。作为"观察者"角色，自动检测并创建问题追踪记录，记录问题开始时间、会话ID等信息。此 skill 设计为在 UserPromptSubmit hook 中自动调用，无需用户主动触发，是 Claude 使用分析系统的数据入口。
metadata:
  version: "2.0.0"
  author: "Claude"
  role: "observer"
  system: "claude-usage-analytics"
  trigger_type: "problem_detection"
---

# Usage Observer - 使用观察者

## Overview

本 Skill 用于**自动检测** Claude Code 会话中的问题，创建问题追踪记录。当用户提到错误、失败、问题等关键词时，本 skill 会自动记录问题开始时间，等待后续 `usage-resolver` skill 检测解决信号后完成记录。

**职责分工：**
- **usage-observer (观察者)**: 检测问题，创建追踪记录，记录开始时间
- **usage-resolver (解决者)**: 检测解决信号，计算耗时，完成数据存储
- **usage-recorder (记录员)**: 接收 resolver 传递的数据，完成实际存储

数据最终存储在用户目录的 `.claude/claude-analysis/` 下，按日期分文件管理。

---

## 执行指令

**当此 skill 被触发时，必须执行以下步骤：**

### Step 1: 分析问题内容

从用户输入中提取以下信息：
1. **问题描述**: 从用户当前提问中提取核心问题
2. **会话阶段**: 根据关键词推断（需求分析/代码编写/调试/测试/部署）
3. **问题类型**: 自动分类（工具错误/理解偏差/执行失败/性能问题/其他）
4. **相关文档**: 提取提及的文件路径（如有）

### Step 2: 创建追踪记录

使用 `state_manager.py` 创建问题追踪记录：

```python
from state_manager import create_problem_entry, add_active_problem

problem_entry = create_problem_entry(
    session_id=params["session_id"],
    problem="[问题描述]",
    stage="[会话阶段]",
    problem_type="[问题类型]",
    user_input=params["user_input"]
)

add_active_problem(problem_entry)
```

### Step 3: 静默完成

**不要向用户显示任何消息**，避免打断工作流程。后台自动完成追踪记录创建。

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

1. **静默执行**: 不向用户显示任何消息，完全后台运行
2. **创建追踪记录**: 只记录开始时间和问题描述，等待解决信号
3. **不调用 recorder**: 数据存储由 `usage-resolver` 完成
4. **状态持久化**: 使用 `tracking_state.json` 跨 Hook 调用共享状态