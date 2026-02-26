# Claude Usage Analysis Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue.svg)](https://code.claude.com)

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 📝 中文介绍

Claude 使用分析系统 - 帮助团队自动采集、分析使用数据，持续优化 Claude Code 使用体验的完整解决方案。

### 🎯 系统概述

这是一个完整的 Claude Code 使用分析系统，通过四个角色协同工作，帮助团队持续优化 Claude Code 的使用体验：

| 角色 | 职责 | 触发方式 |
|------|------|----------|
| 👁️ **Observer (观察者)** | 自动检测问题关键词，采集基础数据 | Hook 自动触发 |
| 📝 **Recorder (记录员)** | 手动记录详细问题信息 | 用户主动调用 |
| 📊 **Analyst (分析师)** | 分析数据，生成洞察报告 | 请求分析 |
| 🎯 **Coach (教练)** | 基于数据提供改进建议 | 寻求建议 |

### 📦 安装

#### 方式 1: 通过 Git URL 安装（推荐）

```bash
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin
```

或安装特定版本：
```bash
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin@v1.0.0
```

#### 方式 2: 手动安装

1. 克隆本仓库：
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
```

2. 在 Claude Code 中添加本地插件：
```bash
claude plugin install ./claude-usage-analysis-plugin
```

#### 方式 3: 通过项目配置自动安装

在项目的 `.claude/CLAUDE.md` 或用户目录 `~/.claude/CLAUDE.md` 中添加：

```markdown
## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin
```

然后在项目目录运行 `claude` 命令时，插件会自动加载。

### ⚙️ 配置

#### 步骤 1: 启用 Hook（自动采集）

在你的 Claude Code 配置中设置 `UserPromptSubmit` hook：

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "错误", "失败", "问题", "报错",
        "error", "exception", "bug", "failed",
        "不对", "错了", "有问题", "crash", "timeout"
      ]
    }
  }
}
```

#### 步骤 2: 开始使用

配置完成后，团队成员正常使用 Claude Code：

1. **自动采集**: 当遇到问题时说"报错了"，系统会自动记录
2. **手动记录**: 说"记录这个问题"补充详细信息
3. **数据分析**: 说"分析本周使用情况"生成报告
4. **改进建议**: 说"给我一些改进建议"获取优化方案

### 📊 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    用户/团队成员                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌────────────────┐
│ 自动采集     │      │ 主动记录       │
│ (Observer)   │      │ (Recorder)     │
└──────┬───────┘      └───────┬────────┘
       │                       │
       └───────────┬───────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   数据存储           │
        │ ~/.claude/claude-analysis/
        └──────────┬──────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌────────────────┐
│ 数据分析     │      │ 改进教练       │
│ (Analyst)    │      │ (Coach)        │
└──────────────┘      └────────────────┘
```

### 🚀 使用示例

#### 场景 1: 自动问题跟踪

```
用户: "运行测试报错了，提示找不到模块"
      ↓
[Hook 自动触发 usage-observer]
      ↓
Claude: "检测到你遇到了问题，我已自动记录：
        - 问题类型: 执行失败
        - 相关文件: 测试文件
        需要我帮你解决这个问题吗？"
```

#### 场景 2: 个人效率分析

```
用户: "分析一下我本周的使用情况"
      ↓
[调用 usage-analyst]
      ↓
Claude: "📊 个人使用周报：
        - 记录数: 12
        - 解决率: 83%
        - 高频问题: 工具错误 (42%)

        💡 建议: 减少工具错误..."
```

#### 场景 3: 团队头脑风暴

```
用户: "我们团队怎么优化 Claude 使用？"
      ↓
[调用 usage-analyst + usage-coach]
      ↓
Claude: "💭 基于团队数据，我们来头脑风暴：

        发现的问题：
        1. Skill description 不清晰（18次）

        可能的解决方案：
        A. 编写培训材料
        B. 建立 Review 机制
        C. 创建模板库

        你觉得哪个方案最适合？"
```

### 📁 数据存储

数据默认存储在用户主目录：

```
~/.claude/claude-analysis/
├── 2024-01-15.md           # 每日记录
├── 2024-01-16.md
├── reports/                # 分析报告
│   ├── weekly_2024-W03.md
│   └── monthly_2024-01.md
├── insights/               # 洞察总结
└── knowledge/              # 知识沉淀
```

### 🔒 隐私说明

- ✅ 数据完全存储在本地，不上传云端
- ✅ 个人数据仅本人可见
- ✅ 团队数据聚合后匿名展示
- ✅ 可配置敏感信息过滤

### 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

<a name="english"></a>
## 📝 English Introduction

Claude Usage Analysis System - A complete solution to help teams automatically collect, analyze usage data, and continuously optimize the Claude Code experience.

### 🎯 System Overview

This is a complete Claude Code usage analytics system with four roles working together:

| Role | Responsibility | Trigger |
|------|----------------|---------|
| 👁️ **Observer** | Auto-detect problem keywords, collect basic data | Hook auto-trigger |
| 📝 **Recorder** | Manually record detailed problem information | User-initiated |
| 📊 **Analyst** | Analyze data, generate insights | On request |
| 🎯 **Coach** | Provide improvement suggestions based on data | Seek advice |

### 📦 Installation

#### Option 1: Install via Git URL (Recommended)

```bash
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin
```

Or install a specific version:
```bash
claude plugin install https://github.com/zhangj1164/claude-usage-analysis-plugin
# 或简写
claude plugin i https://github.com/zhangj1164/claude-usage-analysis-plugin@v1.0.0
```

#### Option 2: Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
```

2. Add the local plugin in Claude Code:
```bash
claude plugin install ./claude-usage-analysis-plugin
```

#### Option 3: Auto-install via Project Configuration

Add to your project's `.claude/CLAUDE.md` or user directory `~/.claude/CLAUDE.md`:

```markdown
## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin
```

The plugin will auto-load when you run `claude` in the project directory.

### ⚙️ Configuration

#### Step 1: Enable Hook (Auto Collection)

Set up the `UserPromptSubmit` hook in your Claude Code configuration:

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "error", "exception", "bug", "failed",
        "wrong", "issue", "crash", "timeout",
        "problem", "not working"
      ]
    }
  }
}
```

#### Step 2: Start Using

After configuration, team members use Claude Code normally:

1. **Auto Collection**: Say "got an error" when problems occur
2. **Manual Record**: Say "record this issue" for detailed logging
3. **Data Analysis**: Say "analyze my weekly usage" for reports
4. **Improvement**: Say "give me suggestions" for optimization tips

### 🔒 Privacy

- ✅ Data stored locally, no cloud upload
- ✅ Personal data visible only to owner
- ✅ Team data anonymized in aggregation
- ✅ Configurable sensitive information filtering

### 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🔗 Links

- [Claude Code Documentation](https://code.claude.com/docs)
- [Agent Skills Specification](https://agentskills.io/specification)
- [Report Issues](../../issues)
- [View Changelog](CHANGELOG.md)

---

Made with ❤️ for Claude Code teams
