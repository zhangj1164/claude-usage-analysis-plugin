#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite - 测试 usage-analytics 插件的完整流程
"""

import json
import sys
import tempfile
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "hooks"))
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "usage-observer" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "usage-resolver" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "usage-recorder" / "scripts"))


def test_state_manager():
    """测试状态管理器"""
    print("\n=== 测试 State Manager ===")

    from state_manager import (
        create_problem_entry,
        add_active_problem,
        get_active_problems,
        resolve_problem,
        load_state,
        save_state
    )

    # 创建测试问题
    entry = create_problem_entry(
        session_id="test_session_123",
        problem="测试问题：这是一个测试",
        stage="调试",
        problem_type="工具错误",
        user_input="测试输入"
    )

    print(f"创建问题: {entry['id']}")
    assert entry["session_id"] == "test_session_123"
    assert entry["status"] == "active"

    # 添加到活动列表
    add_active_problem(entry)
    print("问题已添加到活动列表")

    # 获取活动问题
    active = get_active_problems("test_session_123")
    print(f"活动问题数: {len(active)}")
    assert len(active) > 0

    # 解决问题
    resolved = resolve_problem(entry["id"], solution="测试解决")
    print(f"问题已解决，耗时: {resolved['elapsed_minutes']} 分钟")
    assert resolved["status"] == "resolved"

    # 验证已从活动列表移除
    active_after = get_active_problems("test_session_123")
    assert len(active_after) < len(active)

    print("✅ State Manager 测试通过")
    return True


def test_keyword_router():
    """测试关键词路由"""
    print("\n=== 测试 Keyword Router ===")

    # 导入关键词列表
    from keyword_router import PROBLEM_KEYWORDS, RESOLUTION_KEYWORDS, contains_keywords

    # 测试问题关键词检测
    test_cases_problem = [
        ("运行报错了", True),
        ("测试失败了", True),
        ("这个有问题", True),
        ("error occurred", True),
        ("今天天气不错", False),
    ]

    for text, expected in test_cases_problem:
        result = contains_keywords(text, PROBLEM_KEYWORDS)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (期望: {expected})")
        assert result == expected

    # 测试解决关键词检测
    test_cases_resolution = [
        ("好了，解决了", True),
        ("谢谢帮忙", True),
        ("fixed!", True),
        ("问题还没解决", False),
    ]

    for text, expected in test_cases_resolution:
        result = contains_keywords(text, RESOLUTION_KEYWORDS)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (期望: {expected})")
        assert result == expected

    print("✅ Keyword Router 测试通过")
    return True


def test_auto_observer():
    """测试自动观察者"""
    print("\n=== 测试 Auto Observer ===")

    from auto_observer import observe_problem

    result = observe_problem(
        user_input="运行测试时出现错误，提示找不到模块",
        session_id="test_session_observer"
    )

    print(f"观察结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    assert result["success"] == True
    assert result["stage"] in ["调试", "测试", "代码编写"]
    assert result["type"] in ["执行失败", "工具错误", "其他"]

    print("✅ Auto Observer 测试通过")
    return True


def test_auto_resolver():
    """测试自动解决者"""
    print("\n=== 测试 Auto Resolver ===")

    from auto_resolver import resolve_and_record

    # 首先创建一个问题
    from auto_observer import observe_problem
    observe_problem(
        user_input="测试问题待解决",
        session_id="test_session_resolver"
    )

    # 然后解决它
    result = resolve_and_record(
        session_id="test_session_resolver",
        user_input="好了，解决了"
    )

    print(f"解决结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    assert result["success"] == True
    assert "elapsed_minutes" in result

    print("✅ Auto Resolver 测试通过")
    return True


def test_record_session():
    """测试会话记录"""
    print("\n=== 测试 Record Session ===")

    from record_session import add_record, get_storage_path

    # 添加测试记录
    result = add_record(
        stage="测试",
        problem="测试问题记录",
        problem_type="其他",
        solution="测试解决方案",
        time=5,
        status="已解决",
        note="自动化测试"
    )

    print(f"记录添加: {'成功' if result else '失败'}")
    assert result == True

    # 检查文件是否存在
    storage_path = get_storage_path()
    print(f"存储路径: {storage_path}")

    print("✅ Record Session 测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Usage Analytics Plugin 测试套件")
    print("=" * 50)

    tests = [
        ("State Manager", test_state_manager),
        ("Keyword Router", test_keyword_router),
        ("Auto Observer", test_auto_observer),
        ("Auto Resolver", test_auto_resolver),
        ("Record Session", test_record_session),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"❌ {name} 测试失败: {e}")

    # 打印总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, error in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status}: {name}")
        if error:
            print(f"   错误: {error}")

    print(f"\n总计: {passed}/{total} 通过")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)