---
name: usage-memory-analyzer
description: 当用户想要查看记忆文件内容、分析记忆数据、生成使用总结报告时触发。提取 ~/.claude/projects/*/memory/*.md 文件内容，结合 usage-analytics 数据，输出用户使用 Claude 的总结报告。
license: MIT
metadata:
  version: "1.0.0"
  author: "Claude"
  role: "memory-analyst"
  system: "claude-usage-analytics"
---

# Usage Memory Analyzer - 记忆文件分析师

## Overview

本 Skill 负责提取和分析记忆文件内容，结合 usage-analytics 的使用数据，生成用户使用 Claude 的总结报告。

**记忆文件来源**:
- `~/.claude/projects/*/memory/*.md` - 各项目的记忆文件
- 包含 user、feedback、project、reference 四种类型的记忆

**数据源整合**:
- 记忆文件：功能开发上下文、问题解决过程
- `~/.claude/claude-analysis/YYYY-MM-DD.md`：每日使用记录
- `~/.claude/claude-analysis/tracking_state.json`：问题追踪状态

---

## 触发条件

当用户表达以下意图时触发：
- "查看记忆文件内容"
- "分析我的使用记忆"
- "生成使用总结报告"
- "我这段时间用 Claude 做了什么"
- "总结我的 Claude 使用轨迹"
- "/usage-memory-analyzer"

---

## 执行指令

**当此 skill 被触发时，执行以下步骤：**

### Step 1: 收集记忆文件

遍历以下目录查找记忆文件：
```
~/.claude/projects/*/memory/*.md
```

读取每个记忆文件的内容，提取 frontmatter 信息：
- `name`: 记忆名称
- `description`: 记忆描述
- `type`: 记忆类型 (user/feedback/project/reference)

### Step 2: 收集使用数据

读取 usage-analytics 数据：
```
~/.claude/claude-analysis/YYYY-MM-DD.md (最近 7 天或 30 天)
~/.claude/claude-analysis/tracking_state.json
```

提取：
- 记录总数、解决率
- 高频问题类型
- 平均解决耗时

### Step 3: 分析报告生成

根据收集的数据生成总结报告，包含：

#### A. 记忆概览
- 记忆总数
- 按类型分类统计
- 按项目分类统计

#### B. 使用轨迹
- 活跃天数
- 记录的问题总数
- 问题解决率
- 高频问题 TOP 5

#### C. 功能开发/问题解决历程
- 按时间线整理记忆文件
- 识别主要开发任务
- 解决的关键问题

#### D. 洞察与建议
- 使用模式分析
- 效率改进建议
- 知识沉淀建议

---

## 记忆文件类型

| 类型 | 说明 | 分析重点 |
|------|------|----------|
| **user** | 用户角色、偏好、职责 | 用户画像、使用场景 |
| **feedback** | 用户反馈的工作方式指导 | 行为模式、偏好设置 |
| **project** | 项目上下文、决策、时间线 | 开发历程、关键决策 |
| **reference** | 外部资源链接 | 常用工具、参考资源 |

---

## 报告输出模板

```markdown
# Claude 使用总结报告

**报告周期**: YYYY-MM-DD ~ YYYY-MM-DD
**生成时间**: YYYY-MM-DD HH:mm

## 📊 概览

| 指标 | 数值 |
|------|------|
| 记忆文件数 | X |
| 活跃天数 | X 天 |
| 记录问题数 | X |
| 问题解决率 | XX% |

## 📁 记忆文件分析

### 按类型分布
- user: X 条
- feedback: X 条
- project: X 条
- reference: X 条

### 按项目分布
- project-a: X 条
- project-b: X 条

## 📈 使用轨迹

### 高频问题类型
1. 工具错误 - X 次
2. 执行失败 - X 次
3. 理解偏差 - X 次

### 解决效率
- 平均解决时间：XX 分钟
- 最快解决：X 分钟
- 最长解决：XX 分钟

## 🛠️ 功能开发历程

### [项目名称]
**时间**: YYYY-MM-DD
**任务**: [功能描述]
**状态**: ✅ 已完成 / 🔄 进行中

关键事件:
- YYYY-MM-DD: 开始开发 X 功能
- YYYY-MM-DD: 解决 X 问题
- YYYY-MM-DD: 功能完成

## 💡 洞察与建议

### 使用模式
- 主要使用时段：[上午/下午/晚上]
- 高频任务类型：[开发/调试/文档]

### 改进建议
1. [具体建议 1]
2. [具体建议 2]

### 知识沉淀
建议将以下内容整理为文档:
- [知识点 1]
- [知识点 2]
```

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

## 示例对话

### 示例 1: 生成周报

**User**: "生成我这周的 Claude 使用报告"

**Claude**:
```
📊 Claude 使用周报

报告周期：2026-03-30 ~ 2026-04-05

【概览】
- 活跃天数：5 天
- 记录问题：12 个
- 解决率：92%
- 平均耗时：18 分钟

【高频问题】
1. 工具错误 - 4 次
2. 执行失败 - 3 次
3. Hook 集成 - 2 次

【功能开发】
✅ h5-code-review Git Hooks 集成
✅ SessionStart Hook 开发
✅ 中文乱码问题修复

【改进建议】
- 工具错误率偏高，建议整理命令速查表
```

### 示例 2: 记忆文件分析

**User**: "查看我都有哪些记忆文件"

**Claude**:
```
📁 记忆文件列表

【user 类型】
- user_role.md - 用户是资深 Go 开发者，前端新手

【feedback 类型】
- feedback_testing.md - 测试必须用真实数据库
- feedback_response_style.md - 回复要简洁直接

【project 类型】
- project_h5_code_review.md - Git Hooks 集成开发
- project_usage_observer_bug.md - 会话继续时 Hook 未触发

【reference 类型】
- reference_pipeline_bugs.md - 管道 bugs 跟踪位置

总计：7 条记忆，覆盖 3 个项目
```

---

## 脚本工具

### analyze_memories.py

```python
#!/usr/bin/env python3
"""提取和分析记忆文件"""

import glob
import yaml
from pathlib import Path
from datetime import datetime

def collect_memories():
    """收集所有记忆文件"""
    memories = []
    pattern = str(Path.home() / '.claude' / 'projects' / '*' / 'memory' / '*.md')
    
    for file_path in glob.glob(pattern):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2]
                
                memories.append({
                    'path': file_path,
                    'project': file_path.split('projects/')[1].split('/memory')[0],
                    'name': frontmatter.get('name', 'Unknown'),
                    'description': frontmatter.get('description', ''),
                    'type': frontmatter.get('type', 'unknown'),
                    'body': body
                })
    
    return memories

def analyze_memories(memories):
    """分析记忆数据"""
    stats = {
        'total': len(memories),
        'by_type': {},
        'by_project': {}
    }
    
    for m in memories:
        # 按类型统计
        t = m['type']
        stats['by_type'][t] = stats['by_type'].get(t, 0) + 1
        
        # 按项目统计
        p = m['project']
        stats['by_project'][p] = stats['by_project'].get(p, 0) + 1
    
    return stats
```

---

## 依赖

- 无第三方依赖
- 可选：PyYAML (解析 frontmatter)

---

## 数据存储位置

| 数据类型 | 存储位置 |
|----------|----------|
| 记忆文件 | `~/.claude/projects/*/memory/*.md` |
| 每日记录 | `~/.claude/claude-analysis/YYYY-MM-DD.md` |
| 追踪状态 | `~/.claude/claude-analysis/tracking_state.json` |
| 分析报告 | `~/.claude/claude-analysis/reports/` |

---

## 注意事项

1. **隐私保护**: 记忆文件可能包含敏感信息，报告生成时注意脱敏
2. **跨项目分析**: 支持多个项目的记忆整合分析
3. **时间范围**: 默认分析最近 7 天，可自定义
4. **增量更新**: 支持基于上次报告的增量分析
