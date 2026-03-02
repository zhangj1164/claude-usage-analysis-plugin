# Claude Usage Analysis Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue.svg)](https://code.claude.com)

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 📝 中文介绍

Claude 使用分析系统 - 帮助团队自动采集、分析使用数据，持续优化 Claude Code 使用体验的完整解决方案。

### 🎯 系统概述

这是一个完整的 Claude Code 使用分析系统，通过五个角色协同工作，帮助团队持续优化 Claude Code 的使用体验：

| 角色 | 职责 | 触发方式 |
|------|------|----------|
| 👁️ **Observer (观察者)** | 检测问题关键词，创建追踪记录 | Hook 自动触发 |
| ✅ **Resolver (解决者)** | 检测解决信号，计算耗费时间 | Hook 自动触发 |
| 📝 **Recorder (记录员)** | 手动记录详细问题信息 | 用户主动调用 |
| 📊 **Analyst (分析师)** | 分析数据，生成洞察报告 | 请求分析 |
| 🎯 **Coach (教练)** | 基于数据提供改进建议 | 寻求建议 |

**✨ v1.1.0 新特性：自动问题追踪**
- 问题出现时自动创建追踪记录
- 检测解决信号后自动计算耗时
- 完全后台运行，无需用户确认
- 静默采集，不打扰工作流程

### 📦 安装

#### 方式 1: 通过 Git URL 安装（推荐）

**步骤 1**: 添加 Marketplace 源
```bash
claude plugin marketplace add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

**步骤 2**: 安装插件（插件名为 `usage-analytics`）
```bash
claude plugin install usage-analytics
# 或简写
claude plugin i usage-analytics
```

#### 方式 2: 本地安装

1. 克隆本仓库：
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
```

2. 添加本地 Marketplace 源并安装：
```bash
claude plugin marketplace add ./claude-usage-analysis-plugin
claude plugin install usage-analytics
```

#### 方式 3: 通过项目配置自动安装

在项目的 `.claude/CLAUDE.md` 或用户目录 `~/.claude/CLAUDE.md` 中添加：

```markdown
## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin
```

然后在项目目录运行 `claude` 命令时，插件会自动加载。

### ⚙️ 配置

插件安装后会自动配置 Hook，无需手动设置。

**Hook 工作流程：**

```
用户输入: "运行报错了"
    ↓
UserPromptSubmit Hook 触发
    ↓
检测问题关键词 → usage-observer 创建追踪记录
    ↓
... 用户解决问题 ...
    ↓
用户输入: "好了，解决了"
    ↓
检测解决信号 → usage-resolver 计算耗时并存储
```

**自动检测关键词：**

| 问题关键词 | 解决信号关键词 |
|-----------|---------------|
| 错误、失败、问题、报错 | 好了、解决了、谢谢 |
| error, exception, bug, failed | done, fixed, works, thanks |

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
│ 问题检测     │      │ 解决检测       │
│ (Observer)   │      │ (Resolver)     │
└──────┬───────┘      └───────┬────────┘
       │                       │
       │  创建追踪记录          │  计算耗时+存储
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

#### 场景 1: 自动问题追踪（v1.1.0 新特性）

```
用户: "运行测试报错了，提示找不到模块"
      ↓
[Hook 自动触发 usage-observer]
      ↓
[后台创建追踪记录，记录开始时间]
      ↓
... 用户与 Claude 交互解决问题 ...
      ↓
用户: "好了，解决了"
      ↓
[Hook 自动触发 usage-resolver]
      ↓
[自动计算耗时，完成数据存储]
      ↓
Claude: (继续正常对话，不打扰用户)
```

**查看自动记录的数据：**
```bash
cat ~/.claude/claude-analysis/$(date +%Y-%m-%d).md
```

#### 场景 2: 手动记录详细信息

```
用户: "记录这个问题：构建失败，花了20分钟解决"
      ↓
[调用 usage-recorder]
      ↓
Claude: "✅ 已记录到 2026-03-02.md
        问题: 构建失败
        耗时: 20分钟
        状态: 已解决"
```

#### 场景 3: 个人效率分析

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

#### 场景 4: 团队头脑风暴

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
├── tracking_state.json     # 问题追踪状态（v1.1.0）
├── reports/                # 分析报告
│   ├── weekly_2024-W03.md
│   └── monthly_2024-01.md
├── insights/               # 洞察总结
└── knowledge/              # 知识沉淀
```

**自动追踪记录示例：**

```markdown
| 时间戳 | 阶段 | 问题 | 类型 | 耗时 | 状态 |
|--------|------|------|------|------|------|
| 10:35 | 调试 | 运行测试报错，找不到模块 | 执行失败 | 5分钟 | 已解决 |
| 14:20 | 代码编写 | Skill 未触发 | 工具错误 | 15分钟 | 已解决 |
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

This is a complete Claude Code usage analytics system with five roles working together:

| Role | Responsibility | Trigger |
|------|----------------|---------|
| 👁️ **Observer** | Detect problem keywords, create tracking records | Hook auto-trigger |
| ✅ **Resolver** | Detect resolution signals, calculate time spent | Hook auto-trigger |
| 📝 **Recorder** | Manually record detailed problem information | User-initiated |
| 📊 **Analyst** | Analyze data, generate insights | On request |
| 🎯 **Coach** | Provide improvement suggestions based on data | Seek advice |

**✨ v1.1.0 New Feature: Automatic Problem Tracking**
- Auto-create tracking records when problems occur
- Auto-calculate time spent when resolution detected
- Fully background operation, no user confirmation needed
- Silent collection, doesn't interrupt workflow

### 📦 Installation

#### Option 1: Install via Git URL (Recommended)

**Step 1**: Add the marketplace source
```bash
claude plugin marketplace add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

**Step 2**: Install the plugin (plugin name is `usage-analytics`)
```bash
claude plugin install usage-analytics
# or shorthand
claude plugin i usage-analytics
```

#### Option 2: Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
```

2. Add local marketplace and install:
```bash
claude plugin marketplace add ./claude-usage-analysis-plugin
claude plugin install usage-analytics
```

#### Option 3: Auto-install via Project Configuration

Add to your project's `.claude/CLAUDE.md` or user directory `~/.claude/CLAUDE.md`:

```markdown
## Plugins

- https://github.com/zhangj1164/claude-usage-analysis-plugin
```

The plugin will auto-load when you run `claude` in the project directory.

### ⚙️ Configuration

Hooks are automatically configured after plugin installation.

**Hook Workflow:**

```
User input: "Got an error when running tests"
    ↓
UserPromptSubmit Hook triggered
    ↓
Problem keywords detected → usage-observer creates tracking record
    ↓
... User solves the problem ...
    ↓
User input: "Fixed, thanks"
    ↓
Resolution signal detected → usage-resolver calculates time and stores
```

**Auto-detection Keywords:**

| Problem Keywords | Resolution Keywords |
|------------------|---------------------|
| 错误、失败、问题、报错 | 好了、解决了、谢谢 |
| error, exception, bug, failed | done, fixed, works, thanks |

### 🔒 Privacy

- ✅ Data stored locally, no cloud upload
- ✅ Personal data visible only to owner
- ✅ Team data anonymized in aggregation
- ✅ Configurable sensitive information filtering

### 📈 Version History

- **v1.1.0** - Automatic problem tracking system
- **v1.0.2** - Windows compatibility fix
- **v1.0.1** - Hook API format fix
- **v1.0.0** - Initial release

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
