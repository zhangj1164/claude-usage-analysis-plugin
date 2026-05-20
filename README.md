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
| ✅ **Resolver (解决者)** | 检测解决信号，更新问题状态 | Hook 自动触发 |
| 📝 **Recorder (记录员)** | 确认问题归档，静默完成 | Hook 自动触发 |
| 📊 **Analyst (分析师)** | 分析数据，生成洞察报告 | 请求分析 |
| 🎯 **Coach (教练)** | 基于数据提供改进建议 | 寻求建议 |

**✨ v2.4.0 新特性：Manifest 规范化与 Wanma Code 支持**
- marketplace.json 新增 `homepage` 和 `repository` 字段
- 移除未识别的 `tags` 和 `icon` 字段，消除验证警告
- 新增 `.wanma-cli-plugin/plugin.json`，支持 Wanma Code 插件体系

**✨ v2.3.0 新特性：SessionStart 和 SessionEnd Hooks**
- 新增 SessionStart hook（matcher: resume|compact）：会话继续时恢复问题追踪
- 新增 SessionEnd hook（matcher: resume|clear）：会话结束时自动记录问题
- 修复 hooks.json 格式（移除 UserPromptSubmit 的 matcher）
- 所有 hook 脚本强制 UTF-8 编码，修复 Windows 下中文乱码
- 完整的生命周期追踪：从会话开始到结束

**✨ v2.2.0 新特性：会话继续时恢复追踪状态**
- SessionStart hook 从 summary 中识别未解决的问题
- 自动恢复到 tracking_state.json 继续追踪
- 形成完整的使用轨迹，即使会话中断/继续也能连贯记录

**✨ v2.1.0 新特性：Hook 强制触发 Skills**
- Hook 通过 additionalContext 强制调用 skills
- 检测问题关键词自动调用 usage-observer
- 检测解决信号自动调用 usage-recorder
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

插件安装后会自动配置 Hooks，无需手动设置。

**完整的 Hooks 架构：**

| Hook 事件 | Matcher | 执行脚本 | 功能 |
|----------|---------|---------|------|
| SessionStart | `resume\|compact` | session_resumer.py | 会话继续时恢复问题追踪 |
| UserPromptSubmit | 无条件 | keyword_router.py | 检测问题关键词，创建追踪 |
| Stop | 无条件 | stop_recorder.py | Claude 回复后自动记录 |
| SessionEnd | `resume\|clear` | session_ender.py | 会话结束时记录并清空 |

**Hook 工作流程：**

```
会话开始/继续 (/resume, /compact)
    ↓
SessionStart Hook 触发
    ↓
从 summary 恢复未解决的问题 → 更新 tracking_state.json
    ↓
用户输入: "运行报错了"
    ↓
UserPromptSubmit Hook 触发
    ↓
检测问题关键词 → 创建追踪记录（后台静默执行）
    ↓
... Claude 回复，用户解决问题 ...
    ↓
Stop Hook 触发
    ↓
自动记录到日期 md 文件
    ↓
用户输入: "好了，解决了"
    ↓
UserPromptSubmit Hook 触发
    ↓
检测解决信号 → 标记问题为 resolved
    ↓
会话结束 (/clear, /resume)
    ↓
SessionEnd Hook 触发
    ↓
记录所有活动问题 → 清空问题列表
```

**自动检测关键词：**

| 问题关键词 | 解决信号关键词 |
|-----------|---------------|
| 错误、失败、问题、报错 | 好了、解决了、谢谢 |
| error, exception, bug, failed | done, fixed, works, thanks |

**静默执行特性：**
- Observer 和 Resolver 在后台自动运行
- 不向用户显示任何消息
- 不打断正常工作流程
- 数据自动存储到本地 md 文件

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

#### 场景 1: 完整的问题追踪生命周期

```
会话继续 (/compact)
    ↓
[SessionStart Hook 触发]
    ↓
从之前会话恢复未解决的问题
    ↓
用户: "运行测试报错了，提示找不到模块"
      ↓
[UserPromptSubmit Hook 检测问题关键词]
      ↓
[创建追踪记录，记录开始时间]
      ↓
... 用户与 Claude 交互解决问题 ...
      ↓
[Stop Hook 触发，自动记录]
      ↓
用户: "好了，解决了"
      ↓
[UserPromptSubmit Hook 检测解决信号]
      ↓
[标记问题为 resolved，计算耗时]
      ↓
会话结束 (/clear)
      ↓
[SessionEnd Hook 触发]
      ↓
[记录所有活动问题到日期 md 文件]
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
用户: "我们团队要复盘，分析一下这些数据"
      ↓
[调用 usage-analyst 团队分析]
      ↓
用户: 提供各成员的 md 文件路径
      ↓
[使用 team_analyzer.py 合并分析]
      ↓
Claude: "📊 团队数据分析报告

        整体概况：
        - 成员数: 3 人
        - 总记录: 45 条
        - 解决率: 82%

        高频问题 TOP 3：
        1. 文件查找困难 (8次)
        2. Skill 未触发 (6次)

        💡 改进建议：
        1. 组织技巧分享会
        2. 优化 Skill 编写规范"
```

**团队数据合并分析：**
```bash
# 合并分析多个成员的 md 文件
python skills/usage-analyst/scripts/team_analyzer.py \
  --merge-files member1.md member2.md member3.md \
  --output team_report.md
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

**团队数据目录结构（用于团队分析）：**
```
team-data/
├── member1/
│   ├── 2024-01-15.md
│   └── 2024-01-16.md
├── member2/
│   ├── 2024-01-15.md
│   └── 2024-01-16.md
└── member3/
    └── 2024-01-15.md
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

- **v2.4.0** - Manifest 规范化，新增 homepage/repository，Wanma Code 支持
- **v2.3.0** - SessionStart 和 SessionEnd hooks，完整生命周期追踪
- **v2.2.0** - 会话继续时恢复问题追踪
- **v2.1.0** - Hook 强制触发 skills，完全后台运行
- **v2.0.0** - SubAgent 架构重构
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
