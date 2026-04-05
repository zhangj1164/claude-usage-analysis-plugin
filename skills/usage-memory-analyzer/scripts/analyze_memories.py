#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆文件提取和分析工具

提取 ~/.claude/projects/*/memory/*.md 文件内容，
结合 usage-analytics 数据，生成用户使用总结报告。
"""

import json
import glob
import re
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


def collect_memories(memory_dir_pattern=None):
    """
    收集所有记忆文件

    Args:
        memory_dir_pattern: 可选，自定义记忆文件目录模式

    Returns:
        记忆文件列表
    """
    memories = []

    if memory_dir_pattern:
        pattern = memory_dir_pattern
    else:
        # 默认模式：~/.claude/projects/*/memory/*.md
        pattern = str(Path.home() / '.claude' / 'projects' / '*' / 'memory' / '*.md')

    for file_path in glob.glob(pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 frontmatter
            frontmatter = {}
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm_text = parts[1]
                    body = parts[2].strip()

                    # 简单解析 YAML frontmatter
                    for line in fm_text.strip().split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip().strip('"\'')

            # 提取项目名
            project = file_path.split('projects' + os.sep)[1].split(os.sep + 'memory')[0] if 'projects' + os.sep in file_path else 'unknown'

            memories.append({
                'path': file_path,
                'project': project,
                'name': frontmatter.get('name', 'Unknown'),
                'description': frontmatter.get('description', ''),
                'type': frontmatter.get('type', 'unknown'),
                'body': body,
                'file_date': datetime.fromtimestamp(Path(file_path).stat().st_mtime)
            })
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")

    return memories


def collect_usage_data(days=7):
    """
    收集 usage-analytics 使用数据

    Args:
        days: 分析最近 N 天

    Returns:
        使用数据字典
    """
    data = {
        'daily_records': [],
        'tracking_state': {},
        'stats': {
            'total_days': 0,
            'total_records': 0,
            'resolved_rate': 0,
            'avg_time': 0
        }
    }

    # 读取每日记录
    analysis_dir = Path.home() / '.claude' / 'claude-analysis'
    cutoff_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        file_path = analysis_dir / f'{date_str}.md'

        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                records = parse_daily_records(content)
                data['daily_records'].append({
                    'date': date_str,
                    'records': records
                })
                data['stats']['total_records'] += len(records)
            except Exception as e:
                print(f"读取每日记录失败 {file_path}: {e}")

    # 读取追踪状态
    state_path = analysis_dir / 'tracking_state.json'
    if state_path.exists():
        try:
            data['tracking_state'] = json.loads(state_path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"读取追踪状态失败 {state_path}: {e}")

    # 计算统计信息
    data['stats']['total_days'] = len(data['daily_records'])

    # 计算解决率和平均耗时
    all_records = []
    for dr in data['daily_records']:
        all_records.extend(dr['records'])

    resolved = [r for r in all_records if r.get('status') == '已解决']
    data['stats']['resolved_rate'] = round(len(resolved) / len(all_records) * 100, 1) if all_records else 0

    times = [r.get('elapsed_minutes', 0) for r in resolved if r.get('elapsed_minutes')]
    data['stats']['avg_time'] = round(sum(times) / len(times), 1) if times else 0

    return data


def parse_daily_records(content):
    """
    解析每日记录文件

    Args:
        content: md 文件内容

    Returns:
        记录列表
    """
    records = []
    lines = content.split('\n')

    in_table = False
    for line in lines:
        if line.startswith('| 时间戳 |') or line.startswith('|-------'):
            in_table = line.startswith('| 时间戳 |')
            continue

        if in_table and line.startswith('|'):
            parts = line.strip('|').split('|')
            if len(parts) >= 9:
                records.append({
                    'time': parts[0].strip(),
                    'stage': parts[1].strip(),
                    'step': parts[2].strip(),
                    'problem': parts[3].strip(),
                    'type': parts[4].strip(),
                    'solution': parts[5].strip(),
                    'elapsed_minutes': float(parts[6].replace('分钟', '').strip()) if parts[6].strip() else 0,
                    'priority': parts[7].strip(),
                    'status': parts[8].strip()
                })

    return records


def analyze_memories(memories):
    """
    分析记忆数据

    Args:
        memories: 记忆文件列表

    Returns:
        分析统计字典
    """
    stats = {
        'total': len(memories),
        'by_type': {},
        'by_project': {},
        'recent': []
    }

    for m in memories:
        # 按类型统计
        t = m['type']
        stats['by_type'][t] = stats['by_type'].get(t, 0) + 1

        # 按项目统计
        p = m['project']
        stats['by_project'][p] = stats['by_project'].get(p, 0) + 1

    # 最近记忆
    sorted_memories = sorted(memories, key=lambda x: x['file_date'], reverse=True)
    stats['recent'] = [
        {'name': m['name'], 'type': m['type'], 'project': m['project'], 'date': m['file_date'].strftime('%Y-%m-%d')}
        for m in sorted_memories[:10]
    ]

    return stats


def generate_report(memories, usage_data, days=7):
    """
    生成总结报告

    Args:
        memories: 记忆文件列表
        usage_data: 使用数据
        days: 分析天数

    Returns:
        Markdown 格式报告
    """
    memory_stats = analyze_memories(memories)
    stats = usage_data['stats']

    report = f"""# Claude 使用总结报告

**报告周期**: {(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 概览

| 指标 | 数值 |
|------|------|
| 记忆文件数 | {memory_stats['total']} |
| 活跃天数 | {stats['total_days']} 天 |
| 记录问题数 | {stats['total_records']} 个 |
| 问题解决率 | {stats['resolved_rate']}% |
| 平均解决耗时 | {stats['avg_time']} 分钟 |

## 📁 记忆文件分析

### 按类型分布
"""

    for t, count in sorted(memory_stats['by_type'].items()):
        report += f"- **{t}**: {count} 条\n"

    report += "\n### 按项目分布\n"
    for p, count in sorted(memory_stats['by_project'].items()):
        report += f"- **{p}**: {count} 条\n"

    report += "\n### 最近记忆\n"
    for m in memory_stats['recent'][:5]:
        report += f"- [{m['type']}] {m['name']} ({m['project']}, {m['date']})\n"

    # 使用轨迹
    report += f"""
## 📈 使用轨迹

### 高频问题类型
"""

    # 统计问题类型
    type_counts = {}
    for dr in usage_data['daily_records']:
        for r in dr['records']:
            t = r.get('type', '其他')
            type_counts[t] = type_counts.get(t, 0) + 1

    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (t, count) in enumerate(sorted_types[:5], 1):
        report += f"{i}. **{t}** - {count} 次\n"

    # 功能开发历程
    report += "\n## 🛠️ 功能开发历程\n"

    # 从 project 类型记忆中提取
    project_memories = [m for m in memories if m['type'] == 'project']
    for pm in project_memories:
        report += f"\n### {pm['name']}\n"
        report += f"**项目**: {pm['project']}\n"
        report += f"**更新时间**: {pm['file_date'].strftime('%Y-%m-%d')}\n\n"

        # 提取关键内容
        body_preview = pm['body'][:500]
        report += f"{body_preview}...\n"

    # 洞察与建议
    report += """
## 💡 洞察与建议

### 使用模式分析
"""

    if stats['avg_time'] > 30:
        report += "- ⚠️ 平均解决时间较长，可能需要提升工具使用效率\n"
    elif stats['avg_time'] < 15:
        report += "- ✅ 解决效率较高，工具使用熟练\n"

    if stats['resolved_rate'] < 80:
        report += "- ⚠️ 解决率有提升空间，建议建立问题排查清单\n"
    elif stats['resolved_rate'] > 95:
        report += "- ✅ 解决率优秀，保持良好习惯\n"

    # 高频问题建议
    if sorted_types and sorted_types[0][0] == '工具错误':
        report += "\n### 工具错误改进建议\n"
        report += "1. 整理常用命令速查表\n"
        report += "2. 复杂操作前先在小范围测试\n"
        report += "3. 参考文档确认参数用法\n"

    report += "\n### 知识沉淀建议\n"
    report += "建议将以下内容整理为文档:\n"
    report += "- 最近解决的关键问题及方案\n"
    report += "- 常用工具和命令的最佳实践\n"

    return report


def main():
    """主函数"""
    import argparse
    import io

    # Windows 下修复 stdout 编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="记忆文件提取和分析工具")
    parser.add_argument("--days", type=int, default=7, help="分析最近 N 天 (默认：7)")
    parser.add_argument("--output", help="输出文件路径 (默认：stdout)")
    parser.add_argument("--memory-pattern", help="自定义记忆文件目录模式")

    args = parser.parse_args()

    # 收集记忆文件
    print("收集记忆文件...", file=sys.stderr)
    memories = collect_memories(args.memory_pattern)
    print(f"找到 {len(memories)} 条记忆", file=sys.stderr)

    # 收集使用数据
    print(f"收集最近{args.days}天的使用数据...", file=sys.stderr)
    usage_data = collect_usage_data(args.days)

    # 生成报告
    print("生成报告...", file=sys.stderr)
    report = generate_report(memories, usage_data, args.days)

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到：{args.output}", file=sys.stderr)
    else:
        # Windows 下直接写入 stdout buffer
        if sys.platform == 'win32':
            sys.stdout.buffer.write(report.encode('utf-8'))
        else:
            print(report)


if __name__ == "__main__":
    import sys
    main()
