---
name: usage-memory-analyzer
description: 当用户想要查看记忆文件内容、分析记忆数据、生成使用总结报告时触发。提取 ~/.claude/projects/*/memory/*.md 文件内容，结合 usage-analytics 数据，输出用户使用 Claude 的总结报告。
license: MIT
metadata:
  version: "1.1.0"
  author: "Claude"
  role: "memory-analyst"
  system: "claude-usage-analytics"
---

# Usage Memory Analyzer - 记忆文件分析师

## Overview

提取和分析记忆文件内容，结合 usage-analytics 使用数据，生成用户使用 Claude 的总结报告。

**数据源整合:**
- 记忆文件：`~/.claude/projects/*/memory/*.md` — user/feedback/project/reference 四种类型
- 使用记录：`~/.claude/claude-analysis/YYYY-MM-DD.md`
- 追踪状态：`~/.claude/claude-analysis/tracking_state.json`

---

## 触发条件

- "查看记忆文件内容" / "分析我的使用记忆"
- "生成使用总结报告" / "我这段时间用 Claude 做了什么"
- "总结我的 Claude 使用轨迹" / `/usage-memory-analyzer`

---

## 执行指令

### Step 1: 收集记忆文件

使用 **Glob 工具**搜索：`~/.claude/projects/*/memory/*.md`

对每个文件使用 **Read 工具**读取内容，提取 frontmatter：
- `name`: 记忆名称
- `description`: 记忆描述
- `type`: 记忆类型 (user/feedback/project/reference)

**如果没有找到记忆文件**：告知用户当前无记忆数据，建议先使用 Claude 一段时间积累数据。

### Step 2: 收集使用数据

使用 **Glob 工具**搜索：`~/.claude/claude-analysis/*.md`

读取最近 7 天（默认）或用户指定范围的日期文件，提取：
- 记录总数、解决率
- 高频问题类型
- 平均解决耗时

**如果没有使用数据**：仅基于记忆文件生成报告，标注"无使用统计数据"。

### Step 3: 生成分析报告

整合两部分数据，输出结构化报告：

#### A. 概览
- 记忆总数（按类型/项目分类）
- 活跃天数、问题解决率

#### B. 使用轨迹
- 高频问题 TOP 5
- 解决效率统计

#### C. 开发历程
- 按时间线整理关键事件
- 识别主要开发任务

#### D. 洞察与建议
- 使用模式分析
- 效率改进建议
- 知识沉淀建议

**如果数据不足以生成某部分**：跳过该部分，不编造内容。

---

## 边界条件

| 场景 | 处理 |
|------|------|
| 无记忆文件 | 告知用户，建议先积累数据 |
| 无使用数据 | 仅基于记忆生成报告 |
| 记忆文件解析失败 | 跳过该文件，继续处理其他 |
| 项目目录无权限 | 跳过该目录，列出可访问的目录 |
| 记忆文件数量过多(>50) | 只读取最近修改的 50 个，提示用户缩小范围 |

---

## 记忆文件类型

| 类型 | 说明 | 分析重点 |
|------|------|----------|
| **user** | 用户角色、偏好、职责 | 用户画像、使用场景 |
| **feedback** | 工作方式指导 | 行为模式、偏好设置 |
| **project** | 项目上下文、决策、时间线 | 开发历程、关键决策 |
| **reference** | 外部资源链接 | 常用工具、参考资源 |

---

## 与系统其他角色的协作

```
usage-observer → 数据采集
        ↓
usage-recorder → 数据存储
        ↓
usage-memory-analyzer (本 skill) → 提取记忆 + 使用数据
        ↓
usage-analyst → 生成统计洞察
        ↓
usage-coach → 制定改进方案
```

---

## 数据存储位置

| 数据类型 | 存储位置 |
|----------|----------|
| 记忆文件 | `~/.claude/projects/*/memory/*.md` |
| 每日记录 | `~/.claude/claude-analysis/YYYY-MM-DD.md` |
| 追踪状态 | `~/.claude/claude-analysis/tracking_state.json` |
