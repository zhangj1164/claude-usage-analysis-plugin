#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Router - UserPromptSubmit Hook 处理脚本
根据用户输入中的关键词，决定调用哪个 skill
"""

import json
import sys
import re

# 问题关键词配置
PROBLEM_KEYWORDS = [
    # 中文
    "错误", "失败", "问题", "报错", "不对", "错了", "有问题",
    "超时", "无法", "不能", "异常", "崩溃", "卡住", "慢",
    # 英文
    "error", "exception", "bug", "failed", "fail", "wrong",
    "issue", "crash", "timeout", "broken", "not working",
    "doesn't work", "isn't working"
]

# 解决信号关键词
RESOLUTION_KEYWORDS = [
    # 中文
    "好了", "解决了", "成功了", "谢谢", "可以了", "没问题了",
    "修好了", "搞定了", "完成了", "弄好了",
    # 英文
    "done", "fixed", "works", "thanks", "solved",
    "working now", "resolved", "it works", "perfect"
]

def contains_keywords(text, keywords):
    """检查文本中是否包含任一关键词（不区分大小写）"""
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def process_input():
    """处理从 stdin 接收的 JSON 输入"""
    try:
        # 读取 stdin (使用 UTF-8 编码)
        input_data = sys.stdin.buffer.read().decode('utf-8')
        data = json.loads(input_data)

        # 获取用户输入
        user_input = data.get("prompt", "")
        session_id = data.get("sessionId", "")

        # 检查结果
        result = {
            "decision": "continue",  # 默认继续正常处理
            "actions": []
        }

        # 优先检测解决信号
        if contains_keywords(user_input, RESOLUTION_KEYWORDS):
            result["actions"].append({
                "type": "invoke_skill",
                "skill": "usage-analytics:usage-resolver",
                "params": {
                    "user_input": user_input,
                    "session_id": session_id,
                    "trigger_type": "resolution"
                }
            })

        # 检测问题关键词
        elif contains_keywords(user_input, PROBLEM_KEYWORDS):
            result["actions"].append({
                "type": "invoke_skill",
                "skill": "usage-analytics:usage-observer",
                "params": {
                    "user_input": user_input,
                    "session_id": session_id,
                    "trigger_type": "problem"
                }
            })

        # 输出结果
        print(json.dumps(result, ensure_ascii=False))
        return 0

    except json.JSONDecodeError as e:
        error_result = {
            "decision": "continue",
            "error": f"Invalid JSON input: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        return 1
    except Exception as e:
        error_result = {
            "decision": "continue",
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    sys.exit(process_input())
