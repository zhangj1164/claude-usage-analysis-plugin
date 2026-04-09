#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Resume Hook - 会话继续时恢复问题追踪状态

当会话从 summary 继续时，分析之前的对话内容，识别未解决的问题并恢复到 tracking_state.json。
这样可以在会话继续后继续追踪问题，形成完整的使用轨迹。

触发时机：SessionStart Hook（新会话/继续会话时）

输入：stdin JSON { "session_id": "...", "summary_path": "..." }
输出：stdout JSON { "hookSpecificOutput": { "hookEventName": "SessionStart", "additionalContext": "..." } }
"""

import json
import sys
import re
import io
from datetime import datetime
from pathlib import Path

# Windows 下强制 stdout 使用 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 问题关键词（用于识别未解决的问题）
PROBLEM_KEYWORDS = [
    "错误", "失败", "问题", "报错", "不对", "错了", "有问题",
    "超时", "无法", "不能", "异常", "崩溃", "卡住", "慢",
    "error", "exception", "bug", "failed", "fail", "wrong",
    "issue", "crash", "timeout", "broken", "not working",
]

# 解决信号（用于识别已解决的问题）
RESOLUTION_KEYWORDS = [
    "好了", "解决了", "成功了", "可以了", "没问题了",
    "修好了", "搞定了", "完成了", "弄好了", "谢谢",
    "done", "fixed", "works", "solved", "thanks",
    "working now", "resolved", "it works"
]


def get_state_path():
    """获取 tracking_state.json 路径"""
    return Path.home() / '.claude' / 'claude-analysis' / 'tracking_state.json'


def load_state():
    """加载追踪状态"""
    state_path = get_state_path()
    if not state_path.exists():
        return {"active_problems": [], "resolved_problems": []}
    try:
        return json.loads(state_path.read_text(encoding='utf-8'))
    except Exception:
        return {"active_problems": [], "resolved_problems": []}


def save_state(state):
    """保存追踪状态"""
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def read_summary(summary_path):
    """读取会话 summary/transcript"""
    if not summary_path:
        return ""
    tp = Path(summary_path)
    if not tp.exists():
        return ""
    try:
        return tp.read_text(encoding='utf-8')
    except Exception:
        return ""


def find_unresolved_problems(summary_text):
    """
    从 summary 中识别未解决的问题

    策略：
    1. 查找包含问题关键词的段落
    2. 检查该段落之后是否有解决信号
    3. 没有解决信号的问题视为未解决
    """
    problems = []

    # 按行分割
    lines = summary_text.split('\n')

    # 追踪当前问题
    current_problem = None
    problem_lines = []

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # 检测是否包含问题关键词
        has_problem = any(kw.lower() in line_lower for kw in PROBLEM_KEYWORDS)

        # 检测是否包含解决信号
        has_resolution = any(kw.lower() in line_lower for kw in RESOLUTION_KEYWORDS)

        if has_problem:
            # 如果之前有问题未解决，先保存
            if current_problem is not None and not has_resolution:
                problems.append({
                    "text": "\n".join(problem_lines),
                    "line": current_problem
                })

            # 开始新问题
            current_problem = i
            problem_lines = [line]

        elif current_problem is not None:
            # 继续收集问题相关行
            problem_lines.append(line)

            # 如果遇到解决信号，标记问题为已解决
            if has_resolution:
                current_problem = None
                problem_lines = []

    # 处理最后一个问题
    if current_problem is not None and problem_lines:
        problems.append({
            "text": "\n".join(problem_lines),
            "line": current_problem
        })

    return problems


def extract_problem_summary(text, max_length=100):
    """从问题文本中提取简短描述"""
    # 移除特殊字符
    text = re.sub(r'[#\*\[\]]', '', text)
    text = text.strip()

    # 截取适当长度
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text


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


def resume_session(session_id, summary_path):
    """
    恢复会话追踪状态

    返回：
    - restored_problems: 恢复的问题列表
    - already_tracked: 已在追踪的问题列表
    """
    # 读取 summary
    summary_text = read_summary(summary_path)
    if not summary_text:
        return [], []

    # 查找未解决的问题
    unresolved = find_unresolved_problems(summary_text)

    if not unresolved:
        return [], []

    # 加载当前状态
    state = load_state()
    existing_problems = state.get("active_problems", [])

    # 检查是否已存在相同问题的追踪
    existing_ids = set(p.get("id") for p in existing_problems)

    restored = []
    already_tracked = []

    for problem in unresolved:
        problem_summary = extract_problem_summary(problem["text"])

        # 检查是否已追踪（避免重复）
        is_duplicate = any(
            problem_summary[:50] in p.get("problem", "") or p.get("problem", "") in problem_summary[:50]
            for p in existing_problems
        )

        if is_duplicate:
            already_tracked.append(problem_summary)
            continue

        # 创建新的追踪条目
        entry = {
            "id": f"p_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "session_id": session_id,
            "problem": problem_summary,
            "stage": detect_stage(problem_summary),
            "type": detect_type(problem_summary),
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "restored_from_summary": True,
            "summary_line": problem["line"]
        }

        existing_problems.append(entry)
        restored.append(problem_summary)

    # 更新状态
    state["active_problems"] = existing_problems
    save_state(state)

    return restored, already_tracked


def process_input():
    """处理 Hook 输入"""
    try:
        # 读取 stdin 输入
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        session_id = data.get("session_id", "")
        summary_path = data.get("summary_path", "")

        # 恢复会话追踪状态
        restored, already_tracked = resume_session(session_id, summary_path)

        # 构建 additionalContext
        context_parts = []

        if restored:
            context_parts.append(
                f"[usage-analytics] 从之前会话中恢复 {len(restored)} 个未解决的问题追踪。"
            )
            context_parts.append(
                "问题追踪已恢复到 tracking_state.json，将在会话结束时自动记录。"
            )

        if already_tracked:
            context_parts.append(
                f"[usage-analytics] {len(already_tracked)} 个问题已在追踪中，无需重复记录。"
            )

        if not context_parts:
            # 没有发现问题，静默通过
            return 0

        # 输出结果
        result = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(context_parts)
            }
        }
        print(json.dumps(result, ensure_ascii=False))

        return 0

    except Exception as e:
        # Hook 出错不应阻断用户操作
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(process_input())
