#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Record Session - 记录会话数据到 Markdown 文件
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_storage_path() -> Path:
    """获取存储路径"""
    import os
    custom_path = os.environ.get('CLAUDE_ANALYSIS_PATH')
    if custom_path:
        return Path(custom_path)
    return Path.home() / '.claude' / 'claude-analysis'


def escape_markdown(text: str) -> str:
    """转义 markdown 特殊字符"""
    if not text:
        return ""
    return text.replace('|', '\|').replace('\n', ' ')


def create_daily_file(file_path: Path, date_str: str) -> None:
    """创建每日记录文件"""
    if not file_path.exists():
        header = f"""# Claude Code 会话记录 - {date_str}

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

| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |
|--------|------|------|------|------|----------|------|--------|------|
"""
        file_path.write_text(header, encoding='utf-8')


def add_record(stage: str, problem: str, problem_type: str = "其他",
               step: str = "", solution: str = "", docs: str = "",
               session: str = "", time: int = 0, priority: str = "中",
               status: str = "待解决", note: str = "",
               date: Optional[str] = None) -> bool:
    """添加记录到当日文件"""
    storage_path = get_storage_path()
    storage_path.mkdir(parents=True, exist_ok=True)

    date_str = date if date else datetime.now().strftime('%Y-%m-%d')
    file_path = storage_path / f"{date_str}.md"

    create_daily_file(file_path, date_str)
    content = file_path.read_text(encoding='utf-8')

    timestamp = datetime.now().strftime('%H:%M')
    record_line = f"| {timestamp} | {escape_markdown(stage)} | {escape_markdown(step)} | {escape_markdown(problem)} | {escape_markdown(problem_type)} | {escape_markdown(solution)} | {time}分钟 | {priority} | {status} |\n"

    lines = content.split('\n')
    new_lines = []
    table_header_found = False

    for line in lines:
        new_lines.append(line)
        if '| 时间戳 |' in line:
            table_header_found = True
        elif table_header_found and '|---' in line:
            new_lines.append(record_line)
            table_header_found = False

    content = '\n'.join(new_lines)

    # 更新统计
    records = re.findall(r'\| \d{2}:\d{2} \|', content)
    record_count = len(records)

    content = re.sub(r'- 记录总数: \d+', f'- 记录总数: {record_count}', content)

    time_matches = re.findall(r'\| (\d+)分钟 \|', content)
    total_time = sum(int(t) for t in time_matches)
    content = re.sub(r'- 总耗时: \d+ 分钟', f'- 总耗时: {total_time} 分钟', content)

    resolved_count = len(re.findall(r'\| 已解决 \|', content))
    unresolved_count = record_count - resolved_count
    content = re.sub(r'- 已解决问题: \d+', f'- 已解决问题: {resolved_count}', content)
    content = re.sub(r'- 待解决问题: \d+', f'- 待解决问题: {unresolved_count}', content)

    file_path.write_text(content, encoding='utf-8')
    return True


def main():
    parser = argparse.ArgumentParser(description='记录会话数据')
    parser.add_argument('--stage', '-s', required=True, help='会话阶段')
    parser.add_argument('--step', help='步骤描述')
    parser.add_argument('--problem', '-p', required=True, help='问题描述')
    parser.add_argument('--type', '-t', default='其他', help='问题类型')
    parser.add_argument('--solution', help='解决方案')
    parser.add_argument('--time', type=int, default=0, help='耗费时间(分钟)')
    parser.add_argument('--status', default='待解决', help='状态')

    args = parser.parse_args()

    success = add_record(
        stage=args.stage,
        problem=args.problem,
        problem_type=args.type,
        step=args.step or "",
        solution=args.solution or "",
        time=args.time,
        status=args.status
    )

    if success:
        date_str = datetime.now().strftime('%Y-%m-%d')
        print(f"Recorded to {date_str}.md: {args.problem}")
    return 0


if __name__ == "__main__":
    exit(main())
