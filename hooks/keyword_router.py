#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Router - UserPromptSubmit Hook
检测用户输入中的问题关键词，通过 additionalContext 引导 Claude 委托 problem-tracker agent。
同时在本地 tracking_state.json 中记录问题开始时间。
支持检测解决信号，更新问题状态并记录结束时间。

输入: stdin JSON { "prompt": "...", "session_id": "...", "transcript_path": "..." }
输出: stdout JSON { "hookSpecificOutput": { "hookEventName": "UserPromptSubmit", "additionalContext": "..." } }
"""

import json
import sys
import os
import io
from datetime import datetime
from pathlib import Path

# Windows 下强制 stdout 使用 UTF-8 编码，避免中文乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROBLEM_KEYWORDS = [
    # 执行错误类
    "错误", "失败", "问题", "报错", "不对", "错了", "有问题",
    "超时", "无法", "不能", "异常", "崩溃", "卡住", "慢",
    "error", "exception", "bug", "failed", "fail", "wrong",
    "issue", "crash", "timeout", "broken", "not working",
    "doesn't work", "isn't working",
    # 文档问题类
    "不一致", "不匹配", "冲突", "矛盾", "命名错误", "命名不规范",
    "缺失", "遗漏", "过时", "未更新", "缺少", "漏掉",
    "inconsistent", "mismatch", "conflict", "missing", "outdated"
]

RESOLUTION_KEYWORDS = [
    "好了", "解决了", "成功了", "可以了", "没问题了",
    "修好了", "搞定了", "完成了", "弄好了", "谢谢",
    "done", "fixed", "works", "solved", "thanks",
    "working now", "resolved", "it works"
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


def mark_problem_resolved(session_id):
    """标记问题已解决，记录结束时间"""
    state_path = get_state_path()
    if not state_path.exists():
        return None

    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
    except Exception:
        return None

    active = state.get("active_problems", [])
    if not active:
        return None

    # 找到最近的活跃问题（同 session）
    resolved_entry = None
    for i, problem in enumerate(active):
        if problem.get("session_id") == session_id:
            resolved_entry = problem
            resolved_entry["end_time"] = datetime.now().isoformat()
            resolved_entry["status"] = "resolved"

            # 计算耗时
            start = datetime.fromisoformat(resolved_entry.get("start_time", ""))
            elapsed = (datetime.now() - start).total_seconds() / 60
            resolved_entry["elapsed_minutes"] = round(elapsed, 1)

            # 从活跃列表移除
            active.pop(i)
            break

    if resolved_entry:
        # 移动到已解决列表
        if "resolved_problems" not in state:
            state["resolved_problems"] = []
        state["resolved_problems"].append(resolved_entry)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

    return resolved_entry


def process_input():
    try:
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        user_input = data.get("prompt", "")
        session_id = data.get("session_id", data.get("sessionId", ""))

        # 优先检测解决信号
        if contains_keywords(user_input, RESOLUTION_KEYWORDS):
            resolved_entry = mark_problem_resolved(session_id)
            if resolved_entry:
                result = {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": (
                            f"[usage-analytics] 检测到问题已解决，耗时 {resolved_entry.get('elapsed_minutes', 0)} 分钟。\n\n"
                            f"**必须执行的操作**：立即调用 /usage-analytics:usage-recorder skill 记录此问题的解决方案。\n"
                            f"问题 ID: {resolved_entry.get('id')} 已归档到 tracking_state.json。\n"
                            f"此操作会在后台静默完成，不影响对用户问题的处理。"
                        )
                    }
                }
                print(json.dumps(result, ensure_ascii=False))
                return 0

        # 检测问题关键词
        if contains_keywords(user_input, PROBLEM_KEYWORDS):
            # 记录问题开始时间到本地文件
            entry = record_problem_start(session_id, user_input)

            # 通过 additionalContext 强制调用 usage-observer skill
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        f"[usage-analytics] 检测到问题关键词，已创建追踪记录 {entry['id']}。\n\n"
                        f"**必须执行的操作**：立即调用 /usage-analytics:usage-observer skill 观察此问题。\n"
                        f"此操作会在后台静默完成，不影响对用户问题的处理。\n"
                        f"问题追踪将由 Stop hook 自动完成记录。"
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
