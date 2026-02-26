#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Session Auto Tracker - 记录会话数据到 markdown 文件
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def get_storage_path():
    """获取存储路径"""
    custom_path = os.environ.get('CLAUDE_ANALYSIS_PATH')
    if custom_path:
        return Path(custom_path)

    # 默认路径
    home = Path.home()
    return home / '.claude' / 'claude-analysis'


def ensure_dir(path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def parse_date(date_str=None):
    """解析日期字符串"""
    if date_str:
        return datetime.strptime(date_str, '%Y-%m-%d')
    return datetime.now()


def get_markdown_file_path(storage_path, date):
    """获取 markdown 文件路径"""
    return storage_path / f"{date.strftime('%Y-%m-%d')}.md"


def parse_existing_records(content):
    """解析已存在的记录"""
    records = []
    lines = content.split('\n')
    in_table = False

    for line in lines:
        if line.startswith('| 时间戳 |'):
            in_table = True
            continue
        if in_table and line.startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 9 and parts[0] != '时间戳':
                # 支持两种格式：旧版9列和完整12列
                record = {
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


def generate_record_row(args, now):
    """生成记录行"""
    timestamp = now.strftime('%H:%M')
    stage = args.stage or '未分类'
    step = args.step or '-'
    problem = args.problem or '-'
    problem_type = args.problem_type or args.type or '其他'
    solution = args.solution or '-'
    docs = args.docs or '-'
    session = args.session or '-'
    time_spent = args.time or '-'
    priority = args.priority or '中'
    status = args.status or '待解决'
    note = args.note or '-'

    return {
        'timestamp': timestamp,
        'stage': stage,
        'step': step,
        'problem': problem,
        'type': problem_type,
        'solution': solution,
        'docs': docs,
        'session': session,
        'time': time_spent,
        'priority': priority,
        'status': status,
        'note': note
    }


def calculate_stats(records):
    """计算统计信息"""
    total = len(records)
    total_time = 0
    solved = 0
    pending = 0
    type_counts = {}

    for r in records:
        # 时间统计
        try:
            if r['time'] and r['time'] != '-':
                total_time += int(r['time'])
        except (ValueError, TypeError):
            pass

        # 状态统计
        if r['status'] == '已解决':
            solved += 1
        elif r['status'] in ['待解决', '需跟进']:
            pending += 1

        # 类型统计
        ptype = r['type'] or '其他'
        type_counts[ptype] = type_counts.get(ptype, 0) + 1

    return {
        'total': total,
        'total_time': total_time,
        'solved': solved,
        'pending': pending,
        'type_counts': type_counts
    }


def generate_markdown_content(date, records, stats, args=None):
    """生成 markdown 内容"""
    date_str = date.strftime('%Y-%m-%d')

    lines = [
        f"# Claude Code 会话记录 - {date_str}",
        "",
        "## 概览",
        "",
        f"- 记录总数: {stats['total']}",
        f"- 总耗时: {stats['total_time']} 分钟",
        f"- 已解决问题: {stats['solved']}",
        f"- 待解决问题: {stats['pending']}",
        "",
        "## 问题分布",
        "",
        "| 类型 | 数量 |",
        "|------|------|",
    ]

    # 问题类型分布
    for ptype, count in sorted(stats['type_counts'].items(), key=lambda x: -x[1]):
        lines.append(f"| {ptype} | {count} |")

    if not stats['type_counts']:
        lines.append("| - | 0 |")

    lines.extend([
        "",
        "## 详细记录",
        "",
        "| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 相关文档 | Session ID | 耗时 | 优先级 | 状态 | 备注 |",
        "|--------|------|------|------|------|----------|----------|------------|------|--------|------|------|",
    ])

    # 记录行
    for r in records:
        docs = r.get('docs', '-')
        session = r.get('session', '-')
        note = r.get('note', '-')
        lines.append(
            f"| {r['timestamp']} | {r['stage']} | {r['step']} | {r['problem']} | "
            f"{r['type']} | {r['solution']} | {docs} | {session} | {r['time']} | {r['priority']} | {r['status']} | {note} |"
        )

    # 自动采集标记
    lines.extend([
        "",
        "---",
        "",
        "*本文件由 claude-usage-analysis-plugin 自动生成*",
    ])

    if args and getattr(args, 'auto_triggered', False):
        lines.append(f"*自动采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='记录 Claude Code 会话数据')
    parser.add_argument('--stage', '-s', help='会话阶段')
    parser.add_argument('--step', help='步骤描述')
    parser.add_argument('--problem', '-p', help='问题描述')
    parser.add_argument('--type', '-t', dest='problem_type', help='问题类型')
    parser.add_argument('--solution', help='解决方案')
    parser.add_argument('--docs', help='相关文档（逗号分隔）')
    parser.add_argument('--session', help='Session ID')
    parser.add_argument('--time', help='耗费时间（分钟）')
    parser.add_argument('--priority', help='优先级（高/中/低）')
    parser.add_argument('--status', help='状态（已解决/待解决/需跟进）')
    parser.add_argument('--note', help='备注')
    parser.add_argument('--date', '-d', help='指定日期（格式：YYYY-MM-DD）')
    parser.add_argument('--auto-triggered', action='store_true', help='标记为自动触发')

    args = parser.parse_args()

    # 检查必需参数
    if not args.problem:
        print("错误: 必须提供问题描述 (--problem)", file=sys.stderr)
        sys.exit(1)

    # 获取存储路径
    storage_path = ensure_dir(get_storage_path())

    # 解析日期
    date = parse_date(args.date)
    md_file = get_markdown_file_path(storage_path, date)

    # 读取已有记录
    existing_records = []
    if md_file.exists():
        content = md_file.read_text(encoding='utf-8')
        existing_records = parse_existing_records(content)

    # 生成新记录
    now = datetime.now()
    new_record = generate_record_row(args, now)

    # 添加新记录
    all_records = existing_records + [new_record]

    # 计算统计
    stats = calculate_stats(all_records)

    # 生成并写入 markdown
    md_content = generate_markdown_content(date, all_records, stats, args)
    md_file.write_text(md_content, encoding='utf-8')

    # 输出结果
    print(f"[OK] 已记录到: {md_file}")
    print(f"     今日记录数: {stats['total']}")
    print(f"     今日总耗时: {stats['total_time']} 分钟")
    print(f"     已解决: {stats['solved']} | 待解决: {stats['pending']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
