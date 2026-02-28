#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Router - UserPromptSubmit Hook 处理脚本
根据用户输入中的关键词，决定调用哪个 skill
"""

import json
import sys
import re

# 关键词配置
KEYWORD_MAP = {
    "usage-observer": [
        # 中文关键词
        "错误", "失败", "问题", "报错", "不对", "错了", "有问题",
        "超时", "无法", "不能", "异常", "崩溃", "卡住", "慢",
        # 英文关键词
        "error", "exception", "bug", "failed", "fail", "wrong",
        "issue", "crash", "timeout", "broken", "not working",
        "doesn't work", "isn't working"
    ]
}

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

        # 检查是否匹配 usage-observer 关键词
        if contains_keywords(user_input, KEYWORD_MAP["usage-observer"]):
            result["actions"].append({
                "type": "skill",
                "skill": "usage-observer",
                "params": {
                    "user_input": user_input,
                    "session_id": session_id
                }
            })
            # 可以选择是否阻止默认处理
            # result["decision"] = "block"

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
