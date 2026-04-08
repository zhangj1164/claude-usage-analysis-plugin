#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Manager - 管理问题追踪状态
持久化存储活动问题，支持跨 Hook 调用
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_state_path() -> Path:
    """获取状态文件路径"""
    storage_path = Path.home() / '.claude' / 'claude-analysis'
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path / 'tracking_state.json'


def load_state() -> Dict[str, Any]:
    """加载当前状态"""
    state_file = get_state_path()
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return {"active_problems": [], "session_history": {}}
    return {"active_problems": [], "session_history": {}}


def save_state(state: Dict[str, Any]) -> None:
    """保存状态"""
    state_file = get_state_path()
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def create_problem_entry(
    session_id: str,
    problem: str,
    stage: str = "未分类",
    problem_type: str = "其他",
    user_input: str = ""
) -> Dict[str, Any]:
    """创建问题条目"""
    return {
        "id": f"{session_id}_{datetime.now().strftime('%H%M%S')}",
        "session_id": session_id,
        "problem": problem,
        "stage": stage,
        "type": problem_type,
        "start_time": datetime.now().isoformat(),
        "user_input": user_input,
        "status": "active"
    }


def add_active_problem(problem_entry: Dict[str, Any]) -> None:
    """添加活动问题"""
    state = load_state()
    state["active_problems"].append(problem_entry)

    # 更新会话历史
    session_id = problem_entry["session_id"]
    if session_id not in state["session_history"]:
        state["session_history"][session_id] = []
    state["session_history"][session_id].append(problem_entry["id"])

    save_state(state)


def get_active_problems(session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取活动问题"""
    state = load_state()
    if session_id:
        return [p for p in state["active_problems"] if p["session_id"] == session_id]
    return state["active_problems"]


def resolve_problem(problem_id: str, solution: str = "") -> Optional[Dict[str, Any]]:
    """解决问题并计算耗时"""
    state = load_state()

    for i, problem in enumerate(state["active_problems"]):
        if problem["id"] == problem_id:
            # 计算耗时
            start_time = datetime.fromisoformat(problem["start_time"])
            end_time = datetime.now()
            elapsed_minutes = int((end_time - start_time).total_seconds() / 60)

            # 更新问题状态
            resolved_problem = problem.copy()
            resolved_problem["end_time"] = end_time.isoformat()
            resolved_problem["elapsed_minutes"] = elapsed_minutes
            resolved_problem["solution"] = solution
            resolved_problem["status"] = "resolved"

            # 从活动列表移除
            state["active_problems"].pop(i)
            save_state(state)

            return resolved_problem

    return None


def cleanup_old_problems(max_age_hours: int = 24) -> None:
    """清理过期的活动问题（避免内存泄漏）"""
    state = load_state()
    current_time = datetime.now()

    active_problems = []
    for problem in state["active_problems"]:
        start_time = datetime.fromisoformat(problem["start_time"])
        age_hours = (current_time - start_time).total_seconds() / 3600

        if age_hours < max_age_hours:
            active_problems.append(problem)

    state["active_problems"] = active_problems
    save_state(state)


if __name__ == "__main__":
    # 测试代码
    print("State Manager Test")

    # 创建测试问题
    test_problem = create_problem_entry(
        session_id="test_session",
        problem="测试问题",
        stage="调试",
        problem_type="工具错误",
        user_input="这是一个测试"
    )

    add_active_problem(test_problem)
    print(f"Added problem: {test_problem['id']}")

    # 查询活动问题
    active = get_active_problems()
    print(f"Active problems: {len(active)}")

    # 解决问题
    resolved = resolve_problem(test_problem["id"], solution="测试解决")
    if resolved:
        print(f"Resolved: {resolved['elapsed_minutes']} minutes")