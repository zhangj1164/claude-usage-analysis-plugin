#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Session Auto Tracker - 查看会话记录
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_storage_path():
    """获取存储路径"""
    custom_path = os.environ.get('CLAUDE_ANALYSIS_PATH')
    if custom_path:
        return Path(custom_path)

    home = Path.home()
    return home / '.claude' / 'claude-analysis'


def parse_records_from_file(md_file):
    """从 markdown 文件解析记录"""
    if not md_file.exists():
        return []

    content = md_file.read_text(encoding='utf-8')
    records = []
    lines = content.split('\n')
    in_table = False
    date_str = md_file.stem  # 文件名即日期

    for line in lines:
        if line.startswith('| 时间戳 |'):
            in_table = True
            continue
        if in_table and line.startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 9 and parts[0] != '时间戳':
                # 支持两种格式：旧版9列和完整12列
                record = {
                    'date': date_str,
                    'timestamp': parts[0],
                    'stage': parts[1],
                    'step': parts[2],
                    'problem': parts[3],
                    'type': parts[4],
                    'solution': parts[5],
                    'time': parts[6] if len(parts) <= 9 else parts[8],
                    'priority': parts[7] if len(parts) <= 9 else parts[9],
                    'status': parts[8] if len(parts) <= 9 else parts[10],
                    'docs': parts[6] if len(parts) > 9 else '-',
                    'session': parts[7] if len(parts) > 9 else '-',
                    'note': parts[11] if len(parts) > 11 else '-'
                }
                records.append(record)

    return records


def get_date_range(start_date, end_date):
    """获取日期范围"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def view_today(storage_path):
    """查看今天"""
    today = datetime.now()
    md_file = storage_path / f"{today.strftime('%Y-%m-%d')}.md"
    return parse_records_from_file(md_file)


def view_date(storage_path, date_str):
    """查看指定日期"""
    md_file = storage_path / f"{date_str}.md"
    return parse_records_from_file(md_file)


def view_week(storage_path):
    """查看本周"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    dates = get_date_range(start_of_week, today)

    all_records = []
    for date in dates:
        md_file = storage_path / f"{date.strftime('%Y-%m-%d')}.md"
        all_records.extend(parse_records_from_file(md_file))

    return all_records


def view_month(storage_path):
    """查看本月"""
    today = datetime.now()
    start_of_month = today.replace(day=1)
    dates = get_date_range(start_of_month, today)

    all_records = []
    for date in dates:
        md_file = storage_path / f"{date.strftime('%Y-%m-%d')}.md"
        all_records.extend(parse_records_from_file(md_file))

    return all_records


def view_all(storage_path):
    """查看所有"""
    all_records = []
    for md_file in sorted(storage_path.glob('*.md')):
        all_records.extend(parse_records_from_file(md_file))
    return all_records


def calculate_stats(records):
    """计算统计信息"""
    total = len(records)
    total_time = 0
    solved = 0
    pending = 0
    type_counts = {}
    stage_counts = {}

    for r in records:
        try:
            if r['time'] and r['time'] != '-':
                total_time += int(r['time'])
        except (ValueError, TypeError):
            pass

        if r['status'] == '已解决':
            solved += 1
        elif r['status'] in ['待解决', '需跟进']:
            pending += 1

        ptype = r['type'] or '其他'
        type_counts[ptype] = type_counts.get(ptype, 0) + 1

        stage = r['stage'] or '未分类'
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    return {
        'total': total,
        'total_time': total_time,
        'solved': solved,
        'pending': pending,
        'type_counts': type_counts,
        'stage_counts': stage_counts
    }


def format_output(records, stats, show_stats=False, title="记录"):
    """格式化输出"""
    print(f"\n{'=' * 60}")
    print(f"📊 {title}")
    print(f"{'=' * 60}")

    if show_stats:
        print(f"\n【统计信息】")
        print(f"  总记录数: {stats['total']}")
        print(f"  总耗时: {stats['total_time']} 分钟")
        print(f"  已解决: {stats['solved']} | 待解决: {stats['pending']}")

        if stats['type_counts']:
            print(f"\n  问题类型分布:")
            for ptype, count in sorted(stats['type_counts'].items(), key=lambda x: -x[1]):
                print(f"    - {ptype}: {count}")

    print(f"\n【详细记录】")
    print("-" * 100)
    print(f"{'时间':<12} {'阶段':<10} {'问题':<30} {'类型':<10} {'状态':<8}")
    print("-" * 100)

    for r in records[-20:]:  # 只显示最近20条
        time_str = f"{r['date']} {r['timestamp']}" if 'date' in r else r['timestamp']
        problem = r['problem'][:28] + '..' if len(r['problem']) > 30 else r['problem']
        print(f"{time_str:<12} {r['stage']:<10} {problem:<30} {r['type']:<10} {r['status']:<8}")

    print("-" * 100)


def main():
    parser = argparse.ArgumentParser(description='查看 Claude Code 会话记录')
    parser.add_argument('--today', '-t', action='store_true', help='查看今天')
    parser.add_argument('--date', '-d', help='指定日期（YYYY-MM-DD）')
    parser.add_argument('--week', '-w', action='store_true', help='查看本周')
    parser.add_argument('--month', '-m', action='store_true', help='查看本月')
    parser.add_argument('--all', '-a', action='store_true', help='查看所有')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--output', '-o', help='输出到文件')

    args = parser.parse_args()

    storage_path = get_storage_path()

    if not storage_path.exists():
        print(f"存储目录不存在: {storage_path}")
        return 1

    # 获取记录
    if args.today:
        records = view_today(storage_path)
        title = "今日记录"
    elif args.date:
        records = view_date(storage_path, args.date)
        title = f"{args.date} 记录"
    elif args.week:
        records = view_week(storage_path)
        title = "本周记录"
    elif args.month:
        records = view_month(storage_path)
        title = "本月记录"
    elif args.all:
        records = view_all(storage_path)
        title = "所有记录"
    else:
        # 默认查看今天
        records = view_today(storage_path)
        title = "今日记录"

    if not records:
        print(f"暂无 {title}")
        return 0

    # 计算统计
    stats = calculate_stats(records)

    # 输出
    if args.output:
        # 保存到文件
        content = f"# {title}\n\n"
        content += f"## 统计\n\n"
        content += f"- 总记录数: {stats['total']}\n"
        content += f"- 总耗时: {stats['total_time']} 分钟\n"
        content += f"- 已解决: {stats['solved']}\n"
        content += f"- 待解决: {stats['pending']}\n\n"

        content += "## 详细记录\n\n"
        content += "| 日期 | 时间 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 相关文档 | Session ID | 耗时 | 状态 |\n"
        content += "|------|------|------|------|------|------|----------|----------|------------|------|------|\n"

        for r in records:
            content += f"| {r.get('date', '-')} | {r['timestamp']} | {r['stage']} | {r.get('step', '-')} | "
            content += f"{r['problem']} | {r['type']} | {r['solution']} | "
            content += f"{r.get('docs', '-')} | {r.get('session', '-')} | {r['time']} | {r['status']} |\n"

        Path(args.output).write_text(content, encoding='utf-8')
        print(f"已导出到: {args.output}")
    else:
        format_output(records, stats, args.stats, title)

    return 0


if __name__ == '__main__':
    sys.exit(main())
