#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Router - UserPromptSubmit Hook
检测用户输入中的问题关键词，通过 additionalContext 引导 Claude 委托 problem-tracker agent。
同时在本地 tracking_state.json 中记录问题开始时间。

输入: stdin JSON { "prompt": "...", "session_id": "...", "transcript_path": "..." }
输出: stdout JSON { "hookSpecificOutput": { "hookEventName": "UserPromptSubmit", "additionalContext": "..." } }
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

PROBLEM_KEYWORDS = [
    "错误", "失败", "问题", "报错", "不对", "错了", "有问题",
    "超时", "无法", "不能", "异常", "崩溃", "卡住", "慢",
    "error", "exception", "bug", "failed", "fail", "wrong",
    "issue", "crash", "timeout", "broken", "not working",
    "doesn't work", "isn't working"
]


def contains_keywords(text, keywords):
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def get_state_path():
    return Path.home() / '.claude' / 'claude-analysis' / 'tracking_state.json'


def record_problem_start(session_id, user_input):
    """在 tracking_state.json 中记录问题开始时间"""
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
        except Exception:
            state = {}

    if "active_problems" not in state:
        state["active_problems"] = []

    problem_desc = user_input.strip()[:100]
    if len(user_input.strip()) > 100:
        problem_desc += "..."

    entry = {
        "id": f"p_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_id": session_id,
        "problem": problem_desc,
        "start_time": datetime.now().isoformat(),
        "status": "active"
    }
    state["active_problems"].append(entry)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    return entry


def process_input():
    try:
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        user_input = data.get("prompt", "")
        session_id = data.get("session_id", data.get("sessionId", ""))

        if contains_keywords(user_input, PROBLEM_KEYWORDS):
            # 记录问题开始时间到本地文件
            entry = record_problem_start(session_id, user_input)

            # 通过 additionalContext 注入指令，引导 Claude 委托 problem-tracker agent
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        f"[usage-analytics] 检测到问题关键词，已创建追踪记录 {entry['id']}。"
                        f"请委托 problem-tracker agent 追踪此问题的处理过程。"
                    )
                }
            }
            print(json.dumps(result, ensure_ascii=False))
        # 未检测到关键词，不输出任何内容（静默通过）

        return 0

    except Exception as e:
        # hook 出错不应阻断用户操作
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(process_input())
