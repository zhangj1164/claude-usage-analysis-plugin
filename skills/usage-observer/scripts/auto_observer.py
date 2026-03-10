#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Observer - 自动观察者脚本
由 usage-observer skill 调用，自动创建问题追踪记录
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 添加 hooks 目录到路径以便导入 state_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "hooks"))
from state_manager import create_problem_entry, add_active_problem

# 阶段识别关键词
STAGE_KEYWORDS = {
    "需求分析": ["需求", "设计", "规划", "分析", "结构", "架构", "方案"],
    "代码编写": ["创建", "编写", "实现", "开发", "写代码", "添加", "修改"],
    "调试": ["调试", "排查", "修复", "bug", "错误", "问题", "报错"],
    "测试": ["测试", "验证", "断言", "用例", "spec"],
    "部署": ["部署", "发布", "上线", "构建", "打包", "CI"]
}

# 问题类型分类
PROBLEM_TYPE_KEYWORDS = {
    "工具错误": ["skill", "工具", "命令", "参数", "未触发", "hook"],
    "理解偏差": ["理解", "意图", "上下文", "误解", "不对"],
    "执行失败": ["失败", "报错", "超时", "崩溃", "异常"],
    "性能问题": ["慢", "超时", "内存", "性能", "卡"],
    "其他": []
}


def detect_stage(user_input: str) -> str:
    """从用户输入推断会话阶段"""
    for stage, keywords in STAGE_KEYWORDS.items():
        for kw in keywords:
            if kw in user_input.lower():
                return stage
    return "未分类"


def detect_problem_type(user_input: str) -> str:
    """从用户输入推断问题类型"""
    input_lower = user_input.lower()
    for ptype, keywords in PROBLEM_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in input_lower:
                return ptype
    return "其他"


def extract_problem_description(user_input: str) -> str:
    """提取问题描述"""
    # 简单处理：截取前100字符
    problem = user_input.strip()
    if len(problem) > 100:
        problem = problem[:100] + "..."
    return problem


def observe_problem(user_input: str, session_id: str) -> dict:
    """观察并创建问题追踪记录"""
    # 分析问题
    stage = detect_stage(user_input)
    problem_type = detect_problem_type(user_input)
    problem = extract_problem_description(user_input)

    # 创建追踪记录
    entry = create_problem_entry(
        session_id=session_id,
        problem=problem,
        stage=stage,
        problem_type=problem_type,
        user_input=user_input
    )

    # 添加到活动问题列表
    add_active_problem(entry)

    return {
        "success": True,
        "problem_id": entry["id"],
        "problem": problem,
        "stage": stage,
        "type": problem_type,
        "start_time": entry["start_time"]
    }


def main():
    parser = argparse.ArgumentParser(description='自动观察者')
    parser.add_argument('--user-input', '-u', required=True, help='用户输入')
    parser.add_argument('--session-id', '-s', required=True, help='会话ID')
    parser.add_argument('--json', action='store_true', help='JSON输出')

    args = parser.parse_args()

    result = observe_problem(args.user_input, args.session_id)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"[Observer] 已追踪问题: {result['problem'][:50]}... (类型: {result['type']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())