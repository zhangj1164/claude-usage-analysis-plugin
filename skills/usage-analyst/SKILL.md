---
name: usage-analyst
description: 当用户需要分析 Claude Code 使用数据时触发。作为"分析师"角色，读取 usage-observer 和 usage-recorder 收集的数据，生成个人/团队的使用洞察报告，包括问题分布、时间趋势、高频问题、解决率分析等。
license: MIT
metadata:
  version: "1.1.0"
  author: "Claude"
  role: "analyst"
  system: "claude-usage-analytics"
  data_source: "~/.claude/claude-analysis/"
---

# Usage Analyst - 使用分析师

## 角色定位

**Usage Analyst** 是 Claude 使用分析系统的**分析节点**，负责读取使用数据并生成多维度洞察报告。

## 触发条件

- "分析一下本周的使用情况" / "生成使用报告"
- "看看团队使用 Claude 的数据" / "分析哪些问题最常见"
- "统计解决率" / "生成周报/月报"

---

## 数据来源

从 `~/.claude/claude-analysis/` 目录读取日期 md 文件。

---

## 工作流程

### Step 1: 确定分析范围

询问用户：
- 分析对象：个人 / 团队
- 时间范围：日 / 周 / 月 / 季度 / 自定义
- 分析深度：概览 / 详细 / 深度

### Step 2: 读取数据

**个人数据**：使用 Glob 工具搜索 `~/.claude/claude-analysis/*.md`，使用 Read 工具读取指定日期范围的文件。

**团队数据**：询问用户提供团队成员的 md 文件路径或团队数据目录，使用 `scripts/team_analyzer.py`：
```bash
python scripts/team_analyzer.py --personal
python scripts/team_analyzer.py --team-dir /path/to/team-data
python scripts/team_analyzer.py --merge-files member1.md member2.md
```

**如果没有数据文件**：告知用户当前无使用记录，建议先正常使用积累数据。

### Step 3: 解析数据

从日期 md 文件中提取 9 列表格数据：
`| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |`

计算核心指标：
- **基础**: 记录总数、总耗时、平均解决时间、解决率
- **质量**: 问题类型分布、重复问题率
- **效率**: 日均记录数、时段分布

### Step 4: 生成报告

根据分析深度输出：

**概览**: 数据概览 + 问题分布 + TOP 3 高频问题
**详细**: 概览 + 趋势对比 + 耗时分析 + 改进建议
**深度**: 详细 + 使用模式分析 + 异常识别 + 知识沉淀建议

---

## 边界条件

| 场景 | 处理 |
|------|------|
| 数据目录不存在 | 告知用户，建议先正常使用积累数据 |
| 指定日期范围无数据 | 扩大范围或告知无数据 |
| 数据格式异常（列数不匹配） | 跳过异常行，记录警告 |
| team_analyzer.py 不存在 | 退化为手动 Read 逐个文件分析 |
| 团队成员未提供数据 | 基于已有数据分析，标注覆盖范围 |

---

## 核心指标

| 类别 | 指标 |
|------|------|
| 基础 | 记录总数、总耗时、平均解决时间、解决率 |
| 质量 | 问题类型分布、重复问题率、返工率 |
| 效率 | 日均记录数、时段分布、工具使用效率 |

---

## HTML 报告生成（可选）

分析完成后可转换为 HTML 查看：
```bash
python scripts/md_to_html.py -i report.md -o report.html
# 或批量转换
python scripts/md_to_html.py --batch
```

---

## 与系统其他角色的协作

```
usage-observer → 采集数据
        ↓
usage-recorder → 存储数据
        ↓
usage-analyst (本 skill) → 生成洞察
        ↓
usage-coach → 制定改进方案
```

---

## 存储位置

- 数据: `~/.claude/claude-analysis/YYYY-MM-DD.md`
- 状态: `~/.claude/claude-analysis/tracking_state.json`
- 报告: `~/.claude/claude-analysis/reports/`
