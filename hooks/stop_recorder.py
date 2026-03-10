#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stop Hook - Claude 回复完成后自动记录问题
当 Claude 完成一轮回复时触发，检查是否有活动问题需要记录到日期文件。

工作流程:
1. 读取 tracking_state.json 中的活动问题
2. 读取 transcript 判断问题是否已解决
3. 将问题记录写入当天日期的 md 文件
4. 从活动问题列表中移除已记录的问题

输入: stdin JSON { "session_id": "...", "transcript_path": "..." }
输出: 无（静默执行）
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path

RESOLUTION_SIGNALS = [
    "好了", "解决了", "成功了", "可以了", "没问题了",
    "修好了", "搞定了", "完成了", "弄好了",
    "done", "fixed", "works", "solved",
    "working now", "resolved", "it works"
]


def get_state_path():
    return Path.home() / '.claude' / 'claude-analysis' / 'tracking_state.json'


def get_daily_file_path(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    path = Path.home() / '.claude' / 'claude-analysis' / f'{date_str}.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_state():
    state_path = get_state_path()
    if not state_path.exists():
        return {"active_problems": []}
    try:
        return json.loads(state_path.read_text(encoding='utf-8'))
    except Exception:
        return {"active_problems": []}


def save_state(state):
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def check_transcript_for_resolution(transcript_path):
    """检查 transcript 最近内容是否包含解决信号"""
    if not transcript_path:
        return False, ""
    tp = Path(transcript_path)
    if not tp.exists():
        return False, ""
    try:
        lines = tp.read_text(encoding='utf-8').strip().split('\n')
        # 检查最后 10 行
        recent = lines[-10:] if len(lines) > 10 else lines
        recent_text = '\n'.join(recent).lower()
        for signal in RESOLUTION_SIGNALS:
            if signal.lower() in recent_text:
                return True, signal
        return False, ""
    except Exception:
        return False, ""


def calc_elapsed_minutes(start_time_str):
    """计算耗时（分钟）"""
    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = (datetime.now() - start).total_seconds() / 60
        return round(elapsed, 1)
    except Exception:
        return 0


def append_to_daily_file(entry):
    """将问题记录追加到当天的 md 文件"""
    file_path = get_daily_file_path()
    now = datetime.now()

    if not file_path.exists():
        # 创建新文件并写入表头
        header = f"""# Claude Code 会话记录 - {now.strftime('%Y-%m-%d')}

## 详细记录

| 时间戳 | 阶段 | 问题 | 类型 | 耗时 | 状态 | Session ID |
|--------|------|------|------|------|------|------------|
"""
        file_path.write_text(header, encoding='utf-8')

    # 追加记录行
    time_str = now.strftime('%H:%M')
    elapsed = entry.get('elapsed_minutes', 0)
    status = entry.get('status', '待确认')
    problem = entry.get('problem', '').replace('|', '\\|').replace('\n', ' ')
    stage = entry.get('stage', '未分类')
    ptype = entry.get('type', '其他')
    session_id = entry.get('session_id', '')[:12]

    row = f"| {time_str} | {stage} | {problem} | {ptype} | {elapsed}分钟 | {status} | {session_id} |\n"

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(row)


def detect_stage(problem_text):
    """从问题描述推断会话阶段"""
    stage_keywords = {
        "需求分析": ["需求", "设计", "规划", "分析", "架构"],
        "代码编写": ["创建", "编写", "实现", "开发", "添加", "修改"],
        "调试": ["调试", "排查", "修复", "bug", "错误", "报错"],
        "测试": ["测试", "验证", "用例", "spec", "test"],
        "部署": ["部署", "发布", "上线", "构建", "打包", "CI"],
    }
    for stage, keywords in stage_keywords.items():
        for kw in keywords:
            if kw in problem_text.lower():
                return stage
    return "未分类"


def detect_type(problem_text):
    """从问题描述推断问题类型"""
    type_keywords = {
        "工具错误": ["skill", "工具", "命令", "hook", "plugin"],
        "理解偏差": ["理解", "意图", "误解"],
        "执行失败": ["失败", "报错", "超时", "崩溃", "异常", "error", "fail"],
        "性能问题": ["慢", "超时", "内存", "性能"],
    }
    for ptype, keywords in type_keywords.items():
        for kw in keywords:
            if kw in problem_text.lower():
                return ptype
    return "其他"


def process_stop():
    try:
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        session_id = data.get("session_id", "")
        transcript_path = data.get("transcript_path", "")

        state = load_state()
        active = state.get("active_problems", [])

        if not active:
            return 0

        resolved, signal = check_transcript_for_resolution(transcript_path)

        # 处理活动问题
        remaining = []
        for problem in active:
            elapsed = calc_elapsed_minutes(problem.get("start_time", ""))

            # 如果已耗时超过 1 分钟（避免误触发立即记录）
            if elapsed < 0.5:
                remaining.append(problem)
                continue

            entry = {
                "problem": problem.get("problem", ""),
                "session_id": problem.get("session_id", ""),
                "start_time": problem.get("start_time", ""),
                "elapsed_minutes": elapsed,
                "stage": detect_stage(problem.get("problem", "")),
                "type": detect_type(problem.get("problem", "")),
                "status": "已解决" if resolved else "处理中",
            }
            append_to_daily_file(entry)

            # 只有已解决的才从列表移除
            if not resolved:
                remaining.append(problem)

        state["active_problems"] = remaining
        save_state(state)

        return 0

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(process_stop())
