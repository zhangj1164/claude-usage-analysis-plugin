#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Team Analyzer - 团队数据分析脚本
读取多个团队成员的 md 文件，合并分析，生成团队报告

支持两种使用模式：
1. 团队管理员模式：指定团队成员数据目录或文件列表
2. 个人模式：分析个人使用数据

团队使用流程：
1. 各成员安装 usage-analytics 插件
2. 正常使用 Claude Code，问题自动记录
3. 定期（如每周）收集成员数据目录或导出文件
4. 管理员运行此脚本生成团队分析报告
5. 使用 usage-coach skill 进行团队复盘和改进
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


def get_default_storage_path() -> Path:
    """获取默认存储路径"""
    return Path.home() / '.claude' / 'claude-analysis'


def parse_markdown_table(content: str) -> List[Dict[str, str]]:
    """解析 markdown 表格，返回记录列表"""
    records = []
    lines = content.split('\n')

    # 找到表格行
    table_lines = []
    in_table = False
    headers = []

    for line in lines:
        line = line.strip()
        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                # 第一行是表头
                headers = [h.strip() for h in line.split('|')[1:-1]]
                in_table = True
            elif '---' in line:
                # 分隔行，跳过
                continue
            else:
                # 数据行
                values = [v.strip() for v in line.split('|')[1:-1]]
                if len(values) == len(headers):
                    record = dict(zip(headers, values))
                    records.append(record)
        else:
            in_table = False

    return records


def parse_markdown_file(file_path: Path) -> Dict[str, Any]:
    """解析单个 markdown 文件"""
    content = file_path.read_text(encoding='utf-8')

    result = {
        "file": str(file_path),
        "date": file_path.stem,
        "records": [],
        "overview": {}
    }

    # 提取概览信息
    overview_match = re.search(r'## 概览\s*(.*?)(?=##|$)', content, re.DOTALL)
    if overview_match:
        overview_text = overview_match.group(1)
        # 提取数字
        count_match = re.search(r'记录总数[:\s]*(\d+)', overview_text)
        time_match = re.search(r'总耗时[:\s]*(\d+)', overview_text)

        result["overview"] = {
            "record_count": int(count_match.group(1)) if count_match else 0,
            "total_time": int(time_match.group(1)) if time_match else 0
        }

    # 解析表格
    result["records"] = parse_markdown_table(content)

    return result


def load_team_data(team_dir: Path, date_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """加载团队成员数据"""
    team_data = []

    if not team_dir.exists():
        return team_data

    # 遍历子目录（每个子目录代表一个团队成员）
    for member_dir in team_dir.iterdir():
        if not member_dir.is_dir():
            continue

        member_name = member_dir.name
        member_records = []

        # 读取所有 md 文件
        for md_file in member_dir.glob('*.md'):
            if md_file.stem == 'tracking_state':
                continue

            # 日期过滤
            if date_range:
                try:
                    file_date = datetime.strptime(md_file.stem, '%Y-%m-%d').date()
                    if file_date < date_range[0] or file_date > date_range[1]:
                        continue
                except ValueError:
                    continue

            data = parse_markdown_file(md_file)
            data["member"] = member_name
            member_records.append(data)

        if member_records:
            team_data.append({
                "member": member_name,
                "records": member_records
            })

    return team_data


def load_personal_data(storage_path: Path, date_range: Optional[tuple] = None) -> Dict[str, Any]:
    """加载个人数据"""
    personal_records = []

    for md_file in storage_path.glob('*.md'):
        if md_file.stem == 'tracking_state':
            continue

        # 日期过滤
        if date_range:
            try:
                file_date = datetime.strptime(md_file.stem, '%Y-%m-%d').date()
                if file_date < date_range[0] or file_date > date_range[1]:
                    continue
            except ValueError:
                continue

        data = parse_markdown_file(md_file)
        personal_records.append(data)

    return {
        "member": "个人",
        "records": personal_records
    }


def analyze_team_data(team_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析团队数据"""
    analysis = {
        "total_members": len(team_data),
        "total_records": 0,
        "total_time": 0,
        "resolved_count": 0,
        "unresolved_count": 0,
        "problem_types": defaultdict(int),
        "stages": defaultdict(int),
        "member_stats": [],
        "high_frequency_problems": defaultdict(int),
        "daily_trend": defaultdict(lambda: {"count": 0, "time": 0})
    }

    all_problems = []

    for member_data in team_data:
        member_stats = {
            "member": member_data["member"],
            "record_count": 0,
            "total_time": 0,
            "resolved": 0,
            "unresolved": 0
        }

        for daily_data in member_data["records"]:
            records = daily_data.get("records", [])
            date = daily_data.get("date", "")

            for record in records:
                analysis["total_records"] += 1
                member_stats["record_count"] += 1

                # 时间统计
                time_str = record.get("耗时", "0")
                time_val = int(re.search(r'\d+', time_str).group()) if re.search(r'\d+', time_str) else 0
                analysis["total_time"] += time_val
                member_stats["total_time"] += time_val

                # 日期趋势
                if date:
                    analysis["daily_trend"][date]["count"] += 1
                    analysis["daily_trend"][date]["time"] += time_val

                # 状态统计
                status = record.get("状态", "")
                if "已解决" in status:
                    analysis["resolved_count"] += 1
                    member_stats["resolved"] += 1
                else:
                    analysis["unresolved_count"] += 1
                    member_stats["unresolved"] += 1

                # 问题类型
                problem_type = record.get("类型", record.get("问题类型", "其他"))
                analysis["problem_types"][problem_type] += 1

                # 会话阶段
                stage = record.get("阶段", "未分类")
                analysis["stages"][stage] += 1

                # 问题收集
                problem = record.get("问题", "")
                if problem:
                    all_problems.append(problem)
                    # 简单关键词提取
                    for keyword in problem.split()[:5]:
                        if len(keyword) > 2:
                            analysis["high_frequency_problems"][keyword] += 1

        analysis["member_stats"].append(member_stats)

    # 计算解决率
    total = analysis["resolved_count"] + analysis["unresolved_count"]
    analysis["resolution_rate"] = (analysis["resolved_count"] / total * 100) if total > 0 else 0

    # 排序高频问题
    analysis["top_problems"] = sorted(
        analysis["high_frequency_problems"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return analysis


def generate_team_report(analysis: Dict[str, Any], output_format: str = "markdown") -> str:
    """生成团队分析报告"""
    if output_format == "json":
        # 转换 defaultdict 为普通 dict
        result = dict(analysis)
        result["problem_types"] = dict(result["problem_types"])
        result["stages"] = dict(result["stages"])
        result["high_frequency_problems"] = dict(result["high_frequency_problems"])
        result["daily_trend"] = dict(result["daily_trend"])
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Markdown 格式
    report = f"""# 团队使用分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 整体概况

| 指标 | 数值 |
|------|------|
| 活跃成员 | {analysis['total_members']} 人 |
| 总记录数 | {analysis['total_records']} 条 |
| 总耗时 | {analysis['total_time']} 分钟 ({analysis['total_time']/60:.1f} 小时) |
| 解决率 | {analysis['resolution_rate']:.1f}% |
| 已解决 | {analysis['resolved_count']} 条 |
| 待解决 | {analysis['unresolved_count']} 条 |

## 成员活跃度

| 成员 | 记录数 | 总耗时(分钟) | 已解决 | 待解决 |
|------|--------|-------------|--------|--------|
"""
    for member in analysis["member_stats"]:
        report += f"| {member['member']} | {member['record_count']} | {member['total_time']} | {member['resolved']} | {member['unresolved']} |\n"

    report += """
## 问题类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
"""
    total_types = sum(analysis["problem_types"].values())
    for ptype, count in sorted(analysis["problem_types"].items(), key=lambda x: x[1], reverse=True):
        pct = count / total_types * 100 if total_types > 0 else 0
        report += f"| {ptype} | {count} | {pct:.1f}% |\n"

    report += """
## 会话阶段分布

| 阶段 | 数量 |
|------|------|
"""
    for stage, count in sorted(analysis["stages"].items(), key=lambda x: x[1], reverse=True):
        report += f"| {stage} | {count} |\n"

    if analysis["top_problems"]:
        report += """
## 高频问题关键词

| 关键词 | 出现次数 |
|--------|----------|
"""
        for keyword, count in analysis["top_problems"][:5]:
            report += f"| {keyword} | {count} |\n"

    report += """
## 改进建议

基于以上分析，建议关注以下方面：

"""
    # 根据数据生成建议
    suggestions = []

    if analysis["unresolved_count"] > analysis["resolved_count"]:
        suggestions.append("⚠️ 待解决问题较多，建议优先处理积压问题")

    top_type = max(analysis["problem_types"].items(), key=lambda x: x[1])[0] if analysis["problem_types"] else None
    if top_type:
        suggestions.append(f"🎯 问题类型 '{top_type}' 占比最高，建议针对性改进")

    avg_time = analysis["total_time"] / analysis["total_records"] if analysis["total_records"] > 0 else 0
    if avg_time > 30:
        suggestions.append(f"⏱️ 平均解决时间 {avg_time:.0f} 分钟，建议优化问题排查流程")

    if suggestions:
        report += "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))
    else:
        report += "✅ 整体表现良好，继续保持！"

    return report


def main():
    parser = argparse.ArgumentParser(description='团队使用数据分析')
    parser.add_argument('--team-dir', '-t', type=str, help='团队数据目录路径')
    parser.add_argument('--personal', '-p', action='store_true', help='分析个人数据')
    parser.add_argument('--start-date', '-s', type=str, help='起始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', '-e', type=str, help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--format', '-f', type=str, default='markdown', choices=['markdown', 'json'], help='输出格式')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    parser.add_argument('--merge-files', '-m', type=str, nargs='+', help='合并分析多个 md 文件')

    args = parser.parse_args()

    date_range = None
    if args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        date_range = (start, end)

    storage_path = get_default_storage_path()
    team_data = []

    # 合并分析多个文件模式
    if args.merge_files:
        for file_path in args.merge_files:
            path = Path(file_path)
            if path.exists() and path.suffix == '.md':
                data = parse_markdown_file(path)
                data["member"] = path.parent.name if path.parent.name else path.stem
                team_data.append({
                    "member": data["member"],
                    "records": [data]
                })
    # 团队目录模式
    elif args.team_dir:
        team_dir = Path(args.team_dir)
        team_data = load_team_data(team_dir, date_range)
    # 个人数据模式
    elif args.personal:
        personal_data = load_personal_data(storage_path, date_range)
        team_data = [personal_data]
    else:
        # 默认加载个人数据
        personal_data = load_personal_data(storage_path, date_range)
        team_data = [personal_data]

    if not team_data:
        print("未找到数据")
        return 1

    # 分析数据
    analysis = analyze_team_data(team_data)

    # 生成报告
    report = generate_team_report(analysis, args.format)

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"报告已保存到: {output_path}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    exit(main())