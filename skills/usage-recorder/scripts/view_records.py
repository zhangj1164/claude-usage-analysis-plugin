#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Session Tracker - 查看会话记录
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def get_storage_path():
    """获取存储路径"""
    custom_path = os.environ.get('CLAUDE_ANALYSIS_PATH')
    if custom_path:
        return Path(custom_path)
    return Path.home() / '.claude' / 'claude-analysis'


def get_all_records(storage_path=None):
    """获取所有记录文件"""
    if storage_path is None:
        storage_path = get_storage_path()

    if not storage_path.exists():
        return []

    records = []
    for md_file in sorted(storage_path.glob('*.md')):
        if md_file.name.startswith('summary'):
            continue
        date_str = md_file.stem
        records.extend(parse_markdown_file(md_file, date_str))

    return records


def parse_markdown_file(md_path, date_str):
    """解析 markdown 文件提取记录"""
    records = []
    content = md_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    in_table = False
    for line in lines:
        line = line.strip()

        # 检测表格开始
        if line.startswith('| 时间戳 '):
            in_table = True
            continue

        # 跳过表头分隔行
        if in_table and '---' in line and line.startswith('|'):
            continue

        # 解析表格行
        if in_table and line.startswith('|') and len(line) > 10:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            # 确保是数据行而不是表头
            if len(parts) >= 11 and parts[0] != '时间戳':
                record = {
                    'date': date_str,
                    'timestamp': parts[0],
                    'stage': parts[1] if len(parts) > 1 else '',
                    'step': parts[2] if len(parts) > 2 else '',
                    'problem': parts[3] if len(parts) > 3 else '',
                    'type': parts[4] if len(parts) > 4 else '',
                    'solution': parts[5] if len(parts) > 5 else '',
                    'docs': parts[6] if len(parts) > 6 else '',
                    'session': parts[7] if len(parts) > 7 else '',
                    'time': parts[8] if len(parts) > 8 else '',
                    'priority': parts[9] if len(parts) > 9 else '',
                    'status': parts[10] if len(parts) > 10 else '',
                    'note': parts[11] if len(parts) > 11 else ''
                }
                records.append(record)

    return records


def filter_by_date(records, date_str):
    """按日期过滤记录"""
    return [r for r in records if r['date'] == date_str]


def filter_by_week(records, year, week):
    """按周过滤记录"""
    filtered = []
    for r in records:
        try:
            record_date = datetime.strptime(r['date'], '%Y-%m-%d')
            if record_date.isocalendar()[0] == year and record_date.isocalendar()[1] == week:
                filtered.append(r)
        except:
            pass
    return filtered


def filter_by_month(records, year, month):
    """按月过滤记录"""
    filtered = []
    for r in records:
        try:
            record_date = datetime.strptime(r['date'], '%Y-%m-%d')
            if record_date.year == year and record_date.month == month:
                filtered.append(r)
        except:
            pass
    return filtered


def calculate_stats(records):
    """计算统计数据"""
    stats = {
        'total_count': len(records),
        'total_time': 0,
        'resolved': 0,
        'pending': 0,
        'follow_up': 0,
        'type_distribution': defaultdict(int),
        'stage_distribution': defaultdict(int),
        'priority_distribution': defaultdict(int),
        'daily_counts': defaultdict(int)
    }

    for r in records:
        # 时间统计
        try:
            time_val = int(r['time']) if r['time'] and r['time'].isdigit() else 0
            stats['total_time'] += time_val
        except:
            pass

        # 状态统计
        status = r.get('status', '')
        if '已解决' in status:
            stats['resolved'] += 1
        elif '待解决' in status:
            stats['pending'] += 1
        elif '需跟进' in status:
            stats['follow_up'] += 1

        # 类型分布
        prob_type = r.get('type', '其他')
        stats['type_distribution'][prob_type] += 1

        # 阶段分布
        stage = r.get('stage', '未分类')
        stats['stage_distribution'][stage] += 1

        # 优先级分布
        priority = r.get('priority', '中')
        stats['priority_distribution'][priority] += 1

        # 每日计数
        stats['daily_counts'][r['date']] += 1

    return stats


def display_records(records, title="记录列表"):
    """显示记录列表"""
    if not records:
        print("没有找到记录")
        return

    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")

    # 表格头部
    print(f"\n{'时间':<12} {'阶段':<10} {'问题':<30} {'类型':<10} {'耗时':<6} {'状态':<8}")
    print('-' * 80)

    for r in records:
        time_str = f"{r['date']} {r['timestamp']}"[:16]
        stage = r['stage'][:8] if r['stage'] else '-'
        problem = r['problem'][:28] if r['problem'] else '-'
        prob_type = r['type'][:8] if r['type'] else '-'
        time_cost = r['time'] if r['time'] else '-'
        status = r['status'][:6] if r['status'] else '-'

        print(f"{time_str:<12} {stage:<10} {problem:<30} {prob_type:<10} {time_cost:<6} {status:<8}")

    print(f"\n共 {len(records)} 条记录")


def display_stats(stats):
    """显示统计信息"""
    print(f"\n{'=' * 80}")
    print("  统计信息")
    print(f"{'=' * 80}")

    print(f"\n基本统计:")
    print(f"  记录总数: {stats['total_count']}")
    print(f"  总耗时: {stats['total_time']} 分钟 ({stats['total_time'] // 60} 小时 {stats['total_time'] % 60} 分钟)")
    print(f"  已解决: {stats['resolved']}")
    print(f"  待解决: {stats['pending']}")
    print(f"  需跟进: {stats['follow_up']}")

    if stats['total_count'] > 0:
        resolve_rate = (stats['resolved'] / stats['total_count']) * 100
        print(f"  解决率: {resolve_rate:.1f}%")

    print(f"\n问题类型分布:")
    for prob_type, count in sorted(stats['type_distribution'].items(), key=lambda x: -x[1]):
        bar = '█' * count
        print(f"  {prob_type:<10} {count:>3} {bar}")

    print(f"\n阶段分布:")
    for stage, count in sorted(stats['stage_distribution'].items(), key=lambda x: -x[1]):
        print(f"  {stage}: {count}")

    print(f"\n优先级分布:")
    for priority in ['高', '中', '低']:
        if priority in stats['priority_distribution']:
            count = stats['priority_distribution'][priority]
            print(f"  {priority}: {count}")


def display_daily_summary(records):
    """显示每日汇总"""
    if not records:
        return

    print(f"\n{'=' * 80}")
    print("  每日汇总")
    print(f"{'=' * 80}")

    daily = defaultdict(lambda: {'count': 0, 'time': 0, 'resolved': 0})

    for r in records:
        date = r['date']
        daily[date]['count'] += 1
        try:
            time_val = int(r['time']) if r['time'] and r['time'].isdigit() else 0
            daily[date]['time'] += time_val
        except:
            pass

        if '已解决' in r.get('status', ''):
            daily[date]['resolved'] += 1

    for date in sorted(daily.keys()):
        data = daily[date]
        print(f"  {date}: {data['count']} 条记录, {data['time']} 分钟, {data['resolved']} 已解决")


def export_to_file(records, output_path):
    """导出记录到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Claude Code 会话记录导出\n\n")
        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"记录总数: {len(records)}\n\n")

        f.write("## 详细记录\n\n")
        f.write("| 日期 | 时间 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |\n")
        f.write("|------|------|------|------|------|------|----------|------|--------|------|\n")

        for r in records:
            f.write(f"| {r['date']} | {r['timestamp']} | {r['stage']} | {r['step']} | "
                    f"{r['problem']} | {r['type']} | {r['solution']} | {r['time']} | "
                    f"{r['priority']} | {r['status']} |\n")

    print(f"\n已导出到: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='查看 Claude Code 会话记录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看今天
  python view_records.py --today

  # 查看指定日期
  python view_records.py --date 2024-01-15

  # 查看本周并显示统计
  python view_records.py --week --stats

  # 查看本月并导出
  python view_records.py --month --output report.md

  # 查看所有记录
  python view_records.py --all
        """
    )

    # 时间范围选项
    parser.add_argument('-t', '--today', action='store_true', help='查看今天')
    parser.add_argument('-d', '--date', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('-w', '--week', action='store_true', help='查看本周')
    parser.add_argument('-m', '--month', action='store_true', help='查看本月')
    parser.add_argument('-a', '--all', action='store_true', help='查看所有历史')

    # 其他选项
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--daily', action='store_true', help='显示每日汇总')
    parser.add_argument('-o', '--output', help='导出到文件')

    args = parser.parse_args()

    storage_path = get_storage_path()

    if not storage_path.exists():
        print(f"存储目录不存在: {storage_path}")
        print("还没有任何记录。使用 record_session.py 创建第一条记录。")
        return 1

    # 获取所有记录
    all_records = get_all_records(storage_path)

    if not all_records:
        print("没有找到任何记录")
        return 0

    # 根据参数过滤
    filtered_records = all_records

    if args.today:
        today = datetime.now().strftime('%Y-%m-%d')
        filtered_records = filter_by_date(all_records, today)
        title = f"今日记录 ({today})"
    elif args.date:
        filtered_records = filter_by_date(all_records, args.date)
        title = f"{args.date} 的记录"
    elif args.week:
        now = datetime.now()
        year, week = now.isocalendar()[:2]
        filtered_records = filter_by_week(all_records, year, week)
        title = f"本周记录 ({year}-W{week:02d})"
    elif args.month:
        now = datetime.now()
        filtered_records = filter_by_month(all_records, now.year, now.month)
        title = f"本月记录 ({now.year}-{now.month:02d})"
    else:
        # 默认显示今天
        today = datetime.now().strftime('%Y-%m-%d')
        filtered_records = filter_by_date(all_records, today)
        title = f"今日记录 ({today})"

    # 导出模式
    if args.output:
        export_to_file(filtered_records, args.output)
        return 0

    # 显示记录
    display_records(filtered_records, title)

    # 显示统计
    if args.stats:
        stats = calculate_stats(filtered_records)
        display_stats(stats)

    # 显示每日汇总
    if args.daily:
        display_daily_summary(filtered_records)

    return 0


if __name__ == '__main__':
    sys.exit(main())
