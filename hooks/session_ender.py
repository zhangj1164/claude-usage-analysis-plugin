#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SessionEnd Hook - 会话结束时记录问题
当用户执行 /compact 或 /clear 时触发，将今天的活动问题记录到日期 md 文件。

工作流程:
1. 读取 tracking_state.json 中的活动问题
2. 将问题记录写入当天日期的 md 文件
3. 清空活动问题列表（会话已结束）

输入: stdin JSON { "session_id": "...", "event": "resume|clear" }
输出: 无（静默执行）
"""

import json
import sys
import os
import io
from datetime import datetime
from pathlib import Path

# Windows 下强制 stdout 使用 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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
        return {"active_problems": [], "resolved_problems": []}
    try:
        return json.loads(state_path.read_text(encoding='utf-8'))
    except Exception:
        return {"active_problems": [], "resolved_problems": []}


def save_state(state):
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


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
        header = f"""# Claude Code 会话记录 - {now.strftime('%Y-%m-%d')}

## 详细记录

| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |
|--------|------|------|------|------|----------|------|--------|------|
"""
        file_path.write_text(header, encoding='utf-8')

    time_str = now.strftime('%H:%M')
    elapsed = entry.get('elapsed_minutes', 0)
    status = entry.get('status', '待确认')
    problem = entry.get('problem', '').replace('|', '\\|').replace('\n', ' ')
    stage = entry.get('stage', '未分类')
    ptype = entry.get('type', '其他')
    step = entry.get('step', '-')
    solution = entry.get('solution', '-')
    priority = entry.get('priority', 'P2')

    row = f"| {time_str} | {stage} | {step} | {problem} | {ptype} | {solution} | {elapsed}分钟 | {priority} | {status} |\n"

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(row)


def process_session_end():
    try:
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        event = data.get("event", "")

        state = load_state()

        # 处理已解决的问题
        resolved = state.get("resolved_problems", [])
        for entry in resolved:
            record = {
                "problem": entry.get("problem", ""),
                "session_id": entry.get("session_id", ""),
                "start_time": entry.get("start_time", ""),
                "elapsed_minutes": entry.get("elapsed_minutes", 0),
                "stage": detect_stage(entry.get("problem", "")),
                "type": detect_type(entry.get("problem", "")),
                "step": "-",
                "solution": "已解决",
                "priority": "P2",
                "status": "已解决",
            }
            append_to_daily_file(record)

        # 处理活跃问题
        active = state.get("active_problems", [])
        for problem in active:
            elapsed = calc_elapsed_minutes(problem.get("start_time", ""))
            record = {
                "problem": problem.get("problem", ""),
                "session_id": problem.get("session_id", ""),
                "start_time": problem.get("start_time", ""),
                "elapsed_minutes": elapsed,
                "stage": detect_stage(problem.get("problem", "")),
                "type": detect_type(problem.get("problem", "")),
                "step": "-",
                "solution": "-",
                "priority": "P2",
                "status": "会话结束",
            }
            append_to_daily_file(record)

        # 清空所有问题列表（会话已结束）
        state["active_problems"] = []
        state["resolved_problems"] = []
        save_state(state)

        return 0

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(process_session_end())