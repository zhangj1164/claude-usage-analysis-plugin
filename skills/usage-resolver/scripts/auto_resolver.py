#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Resolver - 自动解决者脚本
由 usage-resolver skill 调用，检测解决信号并完成记录
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加 hooks 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "hooks"))
from state_manager import get_active_problems, resolve_problem

# 添加 usage-recorder scripts 目录
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "usage-recorder" / "scripts"))


def extract_solution(user_input: str) -> str:
    """从用户输入提取解决方案描述"""
    # 简单处理
    if "解决" in user_input or "修好" in user_input:
        return "用户确认已解决"
    return "已解决"


def resolve_and_record(session_id: str, user_input: str) -> dict:
    """解决问题并记录"""
    # 获取当前会话的活动问题
    active_problems = get_active_problems(session_id)

    if not active_problems:
        # 尝试获取所有活动问题（可能是同一个会话）
        active_problems = get_active_problems()

    if not active_problems:
        return {
            "success": False,
            "message": "没有找到活动问题"
        }

    # 取最近的问题
    latest_problem = active_problems[-1]
    solution = extract_solution(user_input)

    # 解决问题（计算耗时）
    resolved = resolve_problem(latest_problem["id"], solution)

    if not resolved:
        return {
            "success": False,
            "message": "解决问题失败"
        }

    # 调用 usage-recorder 记录
    try:
        from record_session import add_record

        add_record(
            stage=resolved.get("stage", "未分类"),
            problem=resolved.get("problem", ""),
            problem_type=resolved.get("type", "其他"),
            solution=solution,
            time=resolved.get("elapsed_minutes", 0),
            status="已解决",
            note="自动追踪"
        )
    except Exception as e:
        # 记录失败不影响主要流程
        print(f"[Resolver] 记录失败: {e}", file=sys.stderr)

    return {
        "success": True,
        "problem_id": resolved["id"],
        "problem": resolved["problem"],
        "elapsed_minutes": resolved["elapsed_minutes"],
        "start_time": resolved["start_time"],
        "end_time": resolved["end_time"]
    }


def main():
    parser = argparse.ArgumentParser(description='自动解决者')
    parser.add_argument('--user-input', '-u', required=True, help='用户输入')
    parser.add_argument('--session-id', '-s', required=True, help='会话ID')
    parser.add_argument('--json', action='store_true', help='JSON输出')

    args = parser.parse_args()

    result = resolve_and_record(args.session_id, args.user_input)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        if result["success"]:
            print(f"[Resolver] 问题已解决: {result['problem'][:50]}... (耗时: {result['elapsed_minutes']}分钟)")
        else:
            print(f"[Resolver] {result['message']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())