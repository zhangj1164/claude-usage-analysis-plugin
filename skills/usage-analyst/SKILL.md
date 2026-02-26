---
name: usage-analyst
description: 当用户需要分析 Claude Code 使用数据时触发。作为"分析师"角色，读取 usage-observer 和 usage-recorder 收集的数据，生成个人/团队的使用洞察报告，包括问题分布、时间趋势、高频问题、解决率分析等。帮助团队识别使用模式和改进机会。是 Claude 使用分析系统的分析节点。
license: MIT
metadata:
  version: "1.0.0"
  author: "Claude"
  role: "analyst"
  system: "claude-usage-analytics"
  data_source: "~/.claude/claude-analysis/"
---

# Usage Analyst - 使用分析师

## 角色定位

**Usage Analyst** 是 Claude 使用分析系统的**分析节点**，负责：
1. 读取采集到的使用数据
2. 生成多维度的分析报告
3. 识别使用模式和问题趋势
4. 为个人和团队提供数据洞察

## 触发条件

当用户表达以下意图时触发：
- "分析一下本周的使用情况"
- "生成使用报告"
- "看看团队使用 Claude 的数据"
- "分析哪些问题最常见"
- "统计解决率"
- "生成周报/月报"

## 数据来源

从以下位置读取数据：
```
~/.claude/claude-analysis/
├── 2024-01-15.md
├── 2024-01-16.md
├── 2024-01-17.md
└── summary/
    └── ...
```

## 分析维度

### 1. 时间维度
- 日报：单日使用情况
- 周报：周趋势分析
- 月报：月度总结
- 季度报：长期趋势

### 2. 个人维度
- 个人使用频率
- 个人问题类型分布
- 个人解决效率
- 个人时间投入

### 3. 团队维度
- 团队整体使用情况
- 成员间对比（匿名）
- 团队协作模式
- 团队知识沉淀

### 4. 问题维度
- 问题类型分布
- 高频问题识别
- 问题解决率
- 问题耗时分析

## 报告类型

### 个人日报
```
📊 个人使用日报 - 2024-01-15

今日概况：
- 记录数: 5
- 总耗时: 120 分钟
- 解决率: 80%

问题分布：
┌──────────┬──────┐
│ 类型     │ 数量 │
├──────────┼──────┤
│ 工具错误 │ 2    │
│ 理解偏差 │ 2    │
│ 执行失败 │ 1    │
└──────────┴──────┘

建议关注：
- 工具错误占比较高，建议 review skill 使用方式
```

### 团队周报
```
📈 团队使用周报 - 2024-W03

整体概况：
- 活跃成员: 8 人
- 总记录数: 45
- 总耗时: 32.5 小时
- 平均解决率: 75%

趋势对比：
- 较上周: +15% 活跃度
- 问题解决率: +5%

TOP 3 高频问题：
1. Skill description 不清晰（12次）
2. 文件查找困难（8次）
3. 测试断言失败（6次）

改进建议：
1. 优化高频 skill 的 description
2. 加强文件查找工具的使用培训
```

### 深度分析报告
```
🔍 深度分析报告 - 2024年1月

使用模式分析：
- 高峰时段: 10:00-12:00, 14:00-17:00
- 平均会话时长: 25 分钟
- 反复出现问题: 3 个

效率分析：
- 平均解决时间: 18 分钟
- 同类问题重复率: 23%
- 最佳实践识别: 5 条

知识沉淀建议：
1. 创建 "常见错误速查表"
2. 编写 "Skill 最佳实践指南"
3. 建立 "问题-解决方案" 知识库
```

## 工作流程

### Step 1: 确定分析范围
询问用户：
- 分析对象：个人 / 团队
- 时间范围：日 / 周 / 月 / 季度 / 自定义
- 分析深度：概览 / 详细 / 深度

### Step 2: 读取数据
使用脚本读取对应时间段的数据：
```bash
python scripts/analyze_usage.py \
  --period week \
  --user personal \
  --output report.md
```

### Step 3: 生成报告
基于数据生成结构化报告：
1. 执行统计分析
2. 识别关键指标
3. 发现趋势和模式
4. 生成可视化描述

### Step 4: 输出洞察
提供：
- 数据概览
- 趋势分析
- 异常识别
- 改进建议

## 脚本使用

### analyze_usage.py - 分析使用数据

**参数：**
- `--period` / `-p`: 时间周期（day/week/month/quarter/custom）
- `--date` / `-d`: 指定日期/起始日期
- `--end-date`: 结束日期（自定义周期）
- `--user` / `-u`: 用户范围（personal/team/all）
- `--type`: 分析类型（overview/detailed/deep）
- `--format` / `-f`: 输出格式（markdown/json/html）
- `--output` / `-o`: 输出文件路径

**示例：**
```bash
# 分析本周个人数据
python scripts/analyze_usage.py --period week --user personal

# 分析团队月度详细报告
python scripts/analyze_usage.py --period month --user team --type detailed

# 导出为 JSON 供其他系统使用
python scripts/analyze_usage.py --period week --format json --output stats.json
```

### md_to_html.py - Markdown 转 HTML

将 Markdown 格式的分析报告转换为美观的 HTML 文件，方便在浏览器中查看。

**参数：**
- `-i`, `--input`: 输入 Markdown 文件路径
- `-o`, `--output`: 输出 HTML 文件路径（可选，默认同目录同名 .html）
- `-d`, `--directory`: 批量转换目录中的所有 Markdown 文件
- `--batch`: 批量转换默认数据目录中的所有报告

**示例：**
```bash
# 转换单个报告
python scripts/md_to_html.py -i report.md
python scripts/md_to_html.py -i report.md -o report.html

# 批量转换目录
python scripts/md_to_html.py -d ./reports
python scripts/md_to_html.py -d ./reports -o ./html_output

# 转换所有分析数据（默认目录）
python scripts/md_to_html.py --batch
```

**HTML 特性：**
- 响应式设计，适配桌面和移动设备
- 美观的卡片式布局
- 表格样式优化，支持悬停效果
- 代码高亮显示
- 打印友好
- 自动生成的页眉和页脚

## 核心指标

### 基础指标
- 记录总数
- 总耗时
- 平均解决时间
- 解决率

### 质量指标
- 问题类型分布
- 重复问题率
- 返工率
- 满意度趋势

### 效率指标
- 平均响应时间
- 问题解决速度
- 工具使用效率
- 知识复用率

## 与系统其他角色的协作

```
usage-observer（观察者）
        ↓ 采集数据
usage-recorder（记录员）
        ↓ 存储数据
usage-analyst（分析师）← 当前角色
        ↓ 生成洞察
usage-coach（教练）
        ↓ 改进建议
用户/团队优化
```

## 输出示例

### 示例 1: 个人周分析

**User:** "分析一下我本周的使用情况"

**Claude:**
```
📊 个人使用周报 (2024-W03)

数据概览：
├─ 记录数: 12
├─ 总耗时: 8.5 小时
├─ 日均: 1.7 小时
└─ 解决率: 83%

问题类型分布：
工具错误    ████████░░  5 (42%)
理解偏差    █████░░░░░  3 (25%)
执行失败    ████░░░░░░  2 (17%)
其他        ██░░░░░░░░  2 (17%)

耗时分析：
├─ 平均解决时间: 21 分钟
├─ 最长耗时: 60 分钟 (调试问题)
└─ 最短耗时: 5 分钟 (简单查询)

本周亮点：
✓ 周三完成 5 个问题，效率最高
✓ Skill 使用熟练度提升

改进机会：
⚠ 周四出现 3 个同类工具错误，建议查看相关文档
⚠ 测试类问题解决耗时较长，建议优化测试流程

建议：
1. 针对高频工具错误创建检查清单
2. 预留更多时间处理调试类问题

💡 **生成 HTML 报告查看：**
```bash
python skills/usage-analyst/scripts/md_to_html.py -i weekly_report.md
# 生成: weekly_report.html
# 用浏览器打开查看美观的报告
```
```

### 示例 2: 团队月分析

**User:** "生成团队月度分析报告"

**Claude:**
```
📈 团队使用月报 (2024-01)

整体概况：
├─ 活跃成员: 12 人
├─ 总记录数: 156
├─ 总耗时: 98 小时
└─ 整体解决率: 78%

成员活跃度：
[████████░░] 成员 A: 28 条
[██████░░░░] 成员 B: 22 条
[█████░░░░░] 成员 C: 18 条
[████░░░░░░] 其他 9 人: 88 条

高频问题 TOP 5：
1. Skill description 优化  (18次, 11.5%)
2. 文件查找困难          (15次, 9.6%)
3. 测试断言失败          (12次, 7.7%)
4. 构建/部署问题         (10次, 6.4%)
5. 依赖安装失败          (8次, 5.1%)

趋势变化：
├─ 活跃度: ↑ 25% (较上月)
├─ 解决率: ↑ 8%
└─ 平均耗时: ↓ 12%

团队建议：
🎯 组织 "Skill description 编写" 培训
🎯 分享文件查找最佳实践
🎯 建立常见测试问题 FAQ
```

## 依赖

- Python 3.7+
- pandas（数据处理，可选）
- matplotlib（图表生成，可选）

## HTML 报告生成

### 使用场景

生成的 HTML 报告适合：
- 在浏览器中查看，界面美观
- 分享给团队成员
- 打印或导出为 PDF
- 存档和演示

### 生成步骤

1. 先生成 Markdown 分析报告（使用 analyze_usage.py 或让 Claude 生成）
2. 使用 md_to_html.py 转换为 HTML
3. 用浏览器打开 HTML 文件

### 完整示例

```bash
# 1. 分析本周数据并生成报告
python scripts/analyze_usage.py --period week --user personal -o weekly_report.md

# 2. 转换为 HTML
python scripts/md_to_html.py -i weekly_report.md -o weekly_report.html

# 3. 在浏览器中打开
# Windows
start weekly_report.html
# Mac
open weekly_report.html
# Linux
xdg-open weekly_report.html
```

### 批量转换所有报告

```bash
# 转换数据目录中的所有 Markdown 文件
python skills/usage-analyst/scripts/md_to_html.py --batch

# HTML 文件将生成在 ~/.claude/claude-analysis/html/
```

## 存储位置

分析结果存储：
- Windows: `%USERPROFILE%\.claude\claude-analysis\reports\`
- Mac/Linux: `~/.claude/claude-analysis/reports/`
