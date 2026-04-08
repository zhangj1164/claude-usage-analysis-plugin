#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""View Records - 查看记录数据"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def get_storage_path() -> Path:
    import os
    custom_path = os.environ.get('CLAUDE_ANALYSIS_PATH')
    if custom_path:
        return Path(custom_path)
    return Path.home() / '.claude' / 'claude-analysis'


def parse_records_from_file(file_path: Path) -> list:
    content = file_path.read_text(encoding='utf-8')
    records = []
    lines = content.split('\n')
    in_table = False
    headers = []

    for line in lines:
        line = line.strip()
        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                headers = [h.strip() for h in line.split('|')[1:-1]]
                in_table = True
            elif '---' in line:
                continue
            else:
                values = [v.strip() for v in line.split('|')[1:-1]]
                if len(values) == len(headers):
                    records.append(dict(zip(headers, values)))
        else:
            in_table = False
    return records


def view_today():
    storage_path = get_storage_path()
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = storage_path / f"{today}.md"

    if not file_path.exists():
        print(f"No records for today ({today})")
        return

    records = parse_records_from_file(file_path)
    print(f"\nDate: {today} ({len(records)} records)\n")
    for r in records:
        print(f"  [{r.get('时间戳', '')}] {r.get('问题', '')[:30]} - {r.get('状态', '')}")


def view_week():
    storage_path = get_storage_path()
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())

    all_records = []
    for i in range(7):
        date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
        file_path = storage_path / f"{date}.md"
        if file_path.exists():
            records = parse_records_from_file(file_path)
            all_records.extend(records)

    print(f"\nThis week: {len(all_records)} records")
    
    types = defaultdict(int)
    for r in all_records:
        types[r.get('类型', r.get('问题类型', '其他'))] += 1
    
    print("\nBy type:")
    for t, c in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {t}: {c}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--today', '-t', action='store_true')
    parser.add_argument('--week', '-w', action='store_true')
    parser.add_argument('--stats', action='store_true')
    args = parser.parse_args()

    if args.week:
        view_week()
    else:
        view_today()
    return 0


if __name__ == "__main__":
    exit(main())
