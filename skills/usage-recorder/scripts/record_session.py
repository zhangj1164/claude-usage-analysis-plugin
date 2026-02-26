#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Session Tracker - 记录会话数据到本地 markdown 文件
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

    # 默认路径：用户主目录/.claude/claude-analysis
    home = Path.home()
    return home / '.claude' / 'claude-analysis'


def ensure_directory(path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_markdown_path(date_str=None):
    """获取指定日期的 markdown 文件路径"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    storage_path = ensure_directory(get_storage_path())
    return storage_path / f'{date_str}.md'


def parse_existing_records(content):
    """解析已有的记录，提取表格数据"""
    records = []
    lines = content.split('\n')
    in_table = False

    for line in lines:
        line = line.strip()
        if line.startswith('| 时间戳 '):
            in_table = True
            continue
        if in_table and line.startswith('|') and '---' in line:
            continue
        if in_table and line.startswith('|') and len(line) > 10:
            # 解析表格行
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 10 and parts[0] != '时间戳':
                records.append(parts)

    return records


def generate_markdown_header(date_str):
    """生成 markdown 文件头部"""
    return f"""# Claude Code 会话记录 - {date_str}

## 概览

- 记录总数: 0
- 总耗时: 0 分钟
- 已解决问题: 0
- 待解决问题: 0

## 问题分布

| 类型 | 数量 |
|------|------|
| 工具错误 | 0 |
| 理解偏差 | 0 |
| 执行失败 | 0 |
| 性能问题 | 0 |
| 其他 | 0 |

## 详细记录

| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 相关文档 | Session ID | 耗时 | 优先级 | 状态 | 备注 |
|--------|------|------|------|------|----------|----------|------------|------|--------|------|------|
"""


def update_summary(content, new_record, is_new_file=False):
    """更新概览统计信息"""
    lines = content.split('\n')
    updated_lines = []

    # 统计变量
    total_records = 0
    total_time = 0
    resolved = 0
    pending = 0
    type_counts = {
        '工具错误': 0,
        '理解偏差': 0,
        '执行失败': 0,
        '性能问题': 0,
        '其他': 0
    }

    # 解析现有记录并统计
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('| 时间戳 '):
            in_table = True
            continue
        if in_table and stripped.startswith('|') and '---' not in stripped and '时间戳' not in stripped:
            parts = [p.strip() for p in stripped.split('|')[1:-1]]
            if len(parts) >= 11:
                total_records += 1
                try:
                    time_val = int(parts[8]) if parts[8].isdigit() else 0
                    total_time += time_val
                except:
                    pass

                status = parts[10] if len(parts) > 10 else ''
                if '已解决' in status:
                    resolved += 1
                elif '待解决' in status or '需跟进' in status:
                    pending += 1

                prob_type = parts[4] if len(parts) > 4 else '其他'
                if prob_type in type_counts:
                    type_counts[prob_type] += 1
                else:
                    type_counts['其他'] += 1

    # 对于新文件，记录已经在表格中，不需要再加1
    # 对于已有文件，需要加1
    if not is_new_file:
        total_records += 1
        try:
            total_time += int(new_record['time']) if new_record.get('time') else 0
        except:
            pass

        if new_record.get('status'):
            if '已解决' in new_record['status']:
                resolved += 1
            elif '待解决' in new_record['status'] or '需跟进' in new_record['status']:
                pending += 1

        if new_record.get('type'):
            if new_record['type'] in type_counts:
                type_counts[new_record['type']] += 1
            else:
                type_counts['其他'] += 1

    # 更新概览行
    for i, line in enumerate(lines):
        if line.startswith('- 记录总数:'):
            updated_lines.append(f'- 记录总数: {total_records}')
        elif line.startswith('- 总耗时:'):
            updated_lines.append(f'- 总耗时: {total_time} 分钟')
        elif line.startswith('- 已解决问题:'):
            updated_lines.append(f'- 已解决问题: {resolved}')
        elif line.startswith('- 待解决问题:'):
            updated_lines.append(f'- 待解决问题: {pending}')
        elif line.startswith('| 工具错误 |'):
            updated_lines.append(f"| 工具错误 | {type_counts['工具错误']} |")
        elif line.startswith('| 理解偏差 |'):
            updated_lines.append(f"| 理解偏差 | {type_counts['理解偏差']} |")
        elif line.startswith('| 执行失败 |'):
            updated_lines.append(f"| 执行失败 | {type_counts['执行失败']} |")
        elif line.startswith('| 性能问题 |'):
            updated_lines.append(f"| 性能问题 | {type_counts['性能问题']} |")
        elif line.startswith('| 其他 |'):
            updated_lines.append(f"| 其他 | {type_counts['其他']} |")
        else:
            updated_lines.append(line)

    return '\n'.join(updated_lines)


def append_record(content, record):
    """追加新记录到表格"""
    timestamp = datetime.now().strftime('%H:%M')

    # 构建表格行
    row = [
        timestamp,
        record.get('stage', ''),
        record.get('step', ''),
        record.get('problem', ''),
        record.get('type', '其他'),
        record.get('solution', ''),
        record.get('docs', ''),
        record.get('session', ''),
        record.get('time', ''),
        record.get('priority', '中'),
        record.get('status', '待解决'),
        record.get('note', '')
    ]

    # 转义表格中的特殊字符，将 None 替换为空字符串
    row = [str(cell).replace('|', '\\|').replace('\n', ' ') if cell is not None else '' for cell in row]

    table_row = '| ' + ' | '.join(row) + ' |'

    # 找到表格结束位置并插入新行
    lines = content.split('\n')
    table_end = len(lines)

    for i, line in enumerate(lines):
        if line.strip().startswith('| 时间戳 '):
            # 找到表头后的分隔行
            if i + 1 < len(lines) and '---' in lines[i + 1]:
                # 找到表格的最后一行
                for j in range(i + 2, len(lines)):
                    if not lines[j].strip().startswith('|'):
                        table_end = j
                        break
                else:
                    table_end = len(lines)

    lines.insert(table_end, table_row)
    return '\n'.join(lines)


def record_session(args):
    """记录会话数据"""
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    md_path = get_markdown_path(date_str)

    # 构建记录数据
    record = {
        'stage': args.stage,
        'step': args.step,
        'problem': args.problem,
        'type': args.type,
        'solution': args.solution,
        'docs': args.docs,
        'session': args.session,
        'time': args.time,
        'priority': args.priority,
        'status': args.status,
        'note': args.note
    }

    # 读取或创建文件
    if md_path.exists():
        content = md_path.read_text(encoding='utf-8')
        content = update_summary(content, record, is_new_file=False)
        content = append_record(content, record)
    else:
        content = generate_markdown_header(date_str)
        content = append_record(content, record)
        content = update_summary(content, record, is_new_file=True)

    # 写入文件
    md_path.write_text(content, encoding='utf-8')

    print(f"[OK] 已记录到: {md_path}")
    print(f"     时间: {datetime.now().strftime('%H:%M')}")
    print(f"     阶段: {record['stage']}")
    print(f"     问题: {record['problem']}")
    return 0


def interactive_record():
    """交互式记录模式"""
    print("=== Claude Session Tracker - 交互式记录 ===\n")

    record = {}

    # 必填字段
    record['stage'] = input("1. 会话阶段 (如: 需求分析/代码编写/调试/测试): ").strip()
    record['problem'] = input("2. 问题描述: ").strip()

    # 选填字段
    record['step'] = input("3. 步骤描述 (可选): ").strip()

    print("\n4. 问题类型:")
    print("   1) 工具错误  2) 理解偏差  3) 执行失败  4) 性能问题  5) 其他")
    type_choice = input("   选择 (1-5, 默认5): ").strip()
    type_map = {
        '1': '工具错误',
        '2': '理解偏差',
        '3': '执行失败',
        '4': '性能问题',
        '5': '其他'
    }
    record['type'] = type_map.get(type_choice, '其他')

    record['solution'] = input("5. 解决方案 (可选): ").strip()
    record['docs'] = input("6. 相关文档路径 (可选): ").strip()
    record['session'] = input("7. Session ID (可选): ").strip()

    time_input = input("8. 耗费时间 - 分钟 (可选): ").strip()
    record['time'] = time_input if time_input.isdigit() else ''

    print("\n9. 优先级: 1) 高  2) 中  3) 低")
    priority_choice = input("   选择 (1-3, 默认2): ").strip()
    priority_map = {'1': '高', '2': '中', '3': '低'}
    record['priority'] = priority_map.get(priority_choice, '中')

    print("\n10. 状态: 1) 已解决  2) 待解决  3) 需跟进")
    status_choice = input("    选择 (1-3, 默认2): ").strip()
    status_map = {'1': '已解决', '2': '待解决', '3': '需跟进'}
    record['status'] = status_map.get(status_choice, '待解决')

    record['note'] = input("11. 备注 (可选): ").strip()

    # 确认
    print("\n--- 记录内容确认 ---")
    for key, value in record.items():
        if value:
            print(f"  {key}: {value}")

    confirm = input("\n确认保存? (Y/n): ").strip().lower()
    if confirm in ('', 'y', 'yes'):
        # 创建临时 args 对象
        class Args:
            pass
        args = Args()
        for key, value in record.items():
            setattr(args, key, value)
        args.date = None

        return record_session(args)
    else:
        print("已取消")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='记录 Claude Code 会话数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式记录
  python record_session.py --interactive

  # 命令行记录
  python record_session.py -s "代码编写" -p "Skill 未触发" -t "工具错误"

  # 完整记录
  python record_session.py \\
    --stage "调试" \\
    --step "运行测试" \\
    --problem "测试失败" \\
    --type "执行失败" \\
    --solution "修改断言" \\
    --time 20 \\
    --priority "高" \\
    --status "已解决"
        """
    )

    parser.add_argument('-i', '--interactive', action='store_true',
                        help='交互式记录模式')

    # 记录字段
    parser.add_argument('-s', '--stage', help='会话阶段（如: 需求分析/代码编写/调试/测试）')
    parser.add_argument('--step', help='步骤描述')
    parser.add_argument('-p', '--problem', help='问题描述')
    parser.add_argument('-t', '--type', default='其他',
                        choices=['工具错误', '理解偏差', '执行失败', '性能问题', '其他'],
                        help='问题类型')
    parser.add_argument('--solution', help='解决方案')
    parser.add_argument('--docs', help='相关文档路径')
    parser.add_argument('--session', help='Session ID')
    parser.add_argument('--time', help='耗费时间（分钟）')
    parser.add_argument('--priority', default='中', choices=['高', '中', '低'],
                        help='优先级')
    parser.add_argument('--status', default='待解决', choices=['已解决', '待解决', '需跟进'],
                        help='状态')
    parser.add_argument('--note', help='备注')
    parser.add_argument('--date', help='指定日期 (格式: YYYY-MM-DD，默认为今天)')

    args = parser.parse_args()

    if args.interactive or (not args.stage and not args.problem):
        return interactive_record()

    if not args.stage or not args.problem:
        print("错误: 阶段(--stage/-s)和问题(--problem/-p)是必填字段")
        parser.print_help()
        return 1

    return record_session(args)


if __name__ == '__main__':
    sys.exit(main())
