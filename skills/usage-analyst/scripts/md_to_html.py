#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to HTML Converter - 将分析报告从 Markdown 转换为 HTML
用于在浏览器中查看分析报告
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


# HTML 模板
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), #3b82f6);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
        }}

        .card h2 {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .card h3 {{
            color: var(--text-primary);
            margin: 20px 0 10px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background-color: var(--bg-color);
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}

        tr:hover {{
            background-color: var(--bg-color);
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary-color);
        }}

        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .badge-success {{
            background-color: #d1fae5;
            color: #065f46;
        }}

        .badge-warning {{
            background-color: #fef3c7;
            color: #92400e;
        }}

        .badge-danger {{
            background-color: #fee2e2;
            color: #991b1b;
        }}

        pre {{
            background-color: #1e293b;
            color: #e2e8f0;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: "Consolas", "Monaco", "Courier New", monospace;
        }}

        code {{
            background-color: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Consolas", "Monaco", "Courier New", monospace;
            font-size: 0.9em;
        }}

        blockquote {{
            border-left: 4px solid var(--primary-color);
            background-color: #f8fafc;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .footer {{
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}

        .chart-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}

        .chart-label {{
            width: 120px;
            font-size: 0.9em;
        }}

        .chart-progress {{
            flex: 1;
            height: 24px;
            background-color: var(--bg-color);
            border-radius: 12px;
            overflow: hidden;
        }}

        .chart-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), #60a5fa);
            border-radius: 12px;
            transition: width 0.3s ease;
        }}

        .chart-value {{
            width: 60px;
            text-align: right;
            font-weight: 600;
            color: var(--text-secondary);
        }}

        @media print {{
            body {{
                background: white;
            }}
            .card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
        <div class="footer">
            <p>Generated by Claude Usage Analysis Plugin</p>
            <p>{timestamp}</p>
        </div>
    </div>
</body>
</html>
"""


def parse_markdown_simple(md_content):
    """简单的 Markdown 解析器"""
    lines = md_content.split('\n')
    html_lines = []
    in_code_block = False
    code_content = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        # 代码块处理
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('<pre><code>' + '\n'.join(code_content) + '</code></pre>')
                code_content = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_content.append(line)
            continue

        # 表格处理
        if '|' in stripped and not stripped.startswith('#'):
            # 跳过分隔行
            if '-+-' in stripped or '---' in stripped.replace('|', '').strip():
                continue

            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            if cells:
                if not html_lines or not html_lines[-1].startswith('<table'):
                    html_lines.append('<table>')
                    html_lines.append('<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead>')
                    html_lines.append('<tbody>')
                else:
                    html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
            continue
        elif html_lines and html_lines[-1].startswith('<table'):
            html_lines.append('</tbody></table>')

        # 列表处理
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            content = stripped[2:]
            html_lines.append(f'<li>{parse_inline_formatting(content)}</li>')
            continue
        elif stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            content = stripped[3:]
            html_lines.append(f'<li>{parse_inline_formatting(content)}</li>')
            continue
        elif in_list and stripped == '':
            html_lines.append(f'</{list_type}>')
            in_list = False
            list_type = None

        # 标题处理
        if stripped.startswith('# '):
            html_lines.append(f'<h1>{parse_inline_formatting(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            html_lines.append(f'<div class="card"><h2>{parse_inline_formatting(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            html_lines.append(f'<h3>{parse_inline_formatting(stripped[4:])}</h3>')
        elif stripped.startswith('#### '):
            html_lines.append(f'<h4>{parse_inline_formatting(stripped[5:])}</h4>')
        # 引用块
        elif stripped.startswith('>'):
            html_lines.append(f'<blockquote>{parse_inline_formatting(stripped[1:].strip())}</blockquote>')
        # 分隔线
        elif stripped == '---' or stripped == '***':
            html_lines.append('</div><div class="card">')
        # 普通段落
        elif stripped:
            html_lines.append(f'<p>{parse_inline_formatting(stripped)}</p>')

    # 关闭未关闭的标签
    if in_code_block:
        html_lines.append('<pre><code>' + '\n'.join(code_content) + '</code></pre>')
    if in_list:
        html_lines.append(f'</{list_type}>')
    if html_lines and html_lines[-1].startswith('<table'):
        html_lines.append('</tbody></table>')

    # 确保最后一个 card 被关闭
    card_count = sum(1 for line in html_lines if '<div class="card">' in line)
    close_count = sum(1 for line in html_lines if '</div>' in line and 'class=' not in line)
    if card_count > close_count:
        html_lines.append('</div>')

    return '\n'.join(html_lines)


def parse_inline_formatting(text):
    """解析行内格式：粗体、斜体、行内代码"""
    import re

    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # 粗体 (**text** 或 __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)

    # 斜体 (*text* 或 _text_)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)

    return text


def extract_title(md_content):
    """从 Markdown 中提取标题"""
    for line in md_content.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return "Analysis Report"


def convert_markdown_to_html(input_path, output_path=None):
    """将 Markdown 文件转换为 HTML"""
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"错误: 文件不存在 {input_path}")
        return False

    # 读取 Markdown 内容
    md_content = input_file.read_text(encoding='utf-8')

    # 解析 Markdown
    html_content = parse_markdown_simple(md_content)

    # 提取标题
    title = extract_title(md_content)

    # 生成时间戳
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 组合完整 HTML
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=html_content,
        timestamp=timestamp
    )

    # 确定输出路径
    if output_path is None:
        output_file = input_file.with_suffix('.html')
    else:
        output_file = Path(output_path)

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 写入 HTML 文件
    output_file.write_text(full_html, encoding='utf-8')

    print(f"[OK] 已转换为 HTML: {output_file}")
    print(f"     原文件: {input_file}")
    print(f"     文件大小: {len(full_html)} 字节")

    return True


def batch_convert(input_dir, output_dir=None):
    """批量转换目录中的所有 Markdown 文件"""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"错误: 目录不存在 {input_dir}")
        return

    # 查找所有 Markdown 文件
    md_files = list(input_path.glob('*.md'))

    if not md_files:
        print(f"未在 {input_dir} 中找到 Markdown 文件")
        return

    print(f"找到 {len(md_files)} 个 Markdown 文件")

    # 确定输出目录
    if output_dir is None:
        output_path = input_path / 'html'
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    # 批量转换
    success_count = 0
    for md_file in md_files:
        output_file = output_path / md_file.with_suffix('.html').name
        if convert_markdown_to_html(md_file, output_file):
            success_count += 1

    print(f"\n批量转换完成: {success_count}/{len(md_files)} 个文件成功")
    print(f"HTML 输出目录: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='将 Markdown 分析报告转换为 HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  python md_to_html.py -i report.md
  python md_to_html.py -i report.md -o report.html

  # 批量转换目录
  python md_to_html.py -d ./reports
  python md_to_html.py -d ./reports -o ./html_output

  # 转换分析数据目录
  python md_to_html.py --batch
        """
    )

    parser.add_argument('-i', '--input', help='输入 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出 HTML 文件路径')
    parser.add_argument('-d', '--directory', help='批量转换目录中的所有 Markdown 文件')
    parser.add_argument('--batch', action='store_true',
                        help='批量转换默认数据目录 (~/.claude/claude-analysis/)')

    args = parser.parse_args()

    # 批量转换默认目录
    if args.batch:
        data_dir = Path.home() / '.claude' / 'claude-analysis'
        if data_dir.exists():
            batch_convert(data_dir)
        else:
            print(f"错误: 默认数据目录不存在 {data_dir}")
            print("请先使用 usage-observer 或 usage-recorder 记录一些数据")
        return

    # 批量转换指定目录
    if args.directory:
        batch_convert(args.directory, args.output)
        return

    # 转换单个文件
    if args.input:
        convert_markdown_to_html(args.input, args.output)
        return

    # 如果没有参数，显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()
