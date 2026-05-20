# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.4.0] - 2026-05-20

### Added
- **marketplace.json**: 新增 `homepage` 和 `repository` 字段
- **.wanma-cli-plugin**: 新增 `plugin.json`，支持 Wanma Code 插件体系

### Changed
- **marketplace.json**: 移除未识别的 `tags` 和 `icon` 字段，清理验证警告
- **.wanma-cli-plugin/marketplace.json**: 同步移除 `tags` 和 `icon`，新增 `homepage` 和 `repository`

## [2.3.0] - 2026-04-05

### Added
- **usage-memory-analyzer**: 新增记忆文件分析 skill
  - 提取 `~/.claude/projects/*/memory/*.md` 文件内容
  - 结合 usage-analytics 使用数据生成总结报告
  - 支持按类型、项目分类统计
  - 生成洞察与改进建议

### Changed
- **marketplace.json**: 添加 usage-memory-analyzer 到 skills 列表

## [2.2.0] - 2026-04-05

### Added
- **SessionStart Hook**: 新增 `hooks/session_resumer.py`，在会话继续时自动恢复问题追踪状态
  - 从 summary 中识别未解决的问题
  - 恢复到 `tracking_state.json`
  - 形成完整的使用轨迹，即使会话中断/继续也能连贯记录
- **会话继续支持**: 解决从 summary 继续会话时 usage-observer 未触发的问题
  - 自动触发 usage-observer 记录问题当前状态
  - 供后续 `/usage-coach` 分析使用轨迹

### Changed
- **marketplace.json**: 添加 SessionStart Hook 配置
- **usage-observer SKILL.md**: 更新说明现在由 UserPromptSubmit 和 SessionStart 两个 Hook 触发
- **usage-observer version**: v4.0.0 → v4.1.0

### Technical Details
- `session_resumer.py` 分析 summary 内容，识别包含问题关键词但未检测到解决信号的段落
- 恢复的问题会标记 `restored_from_summary: true` 字段
- 避免重复追踪：检查问题描述是否已存在于 active_problems

## [2.1.0] - 2026-03-30

### Changed
- **Hook 自动触发 Skills**: Hook 通过 additionalContext 直接调用 skills
  - 检测问题关键词时，强制调用 `/usage-analytics:usage-observer`
  - 检测解决信号时，强制调用 `/usage-analytics:usage-recorder`
  - 使用强制性指令确保 Claude 执行 skills
  - 移除中间 agent 环节，提高触发可靠性

### Removed
- **Agent 架构**: 移除 problem-tracker agent 中间层
  - 从 "Hook → agent → skills" 改为 "Hook → skills"
  - 简化架构，减少故障点

### Updated
- **usage-observer** v3.0.0 → v4.0.0
  - 描述改为"由 UserPromptSubmit hook 自动调用"
  - `trigger_type: automatic`
- **usage-recorder** v1.0.0 → v2.0.0
  - 简化为自动触发场景
  - `trigger_type: automatic`

## [2.0.0] - 2026-03-10

### Added
- **problem-tracker Agent**: SubAgent 定义文件
  - `agents/problem-tracker.md` 带 YAML frontmatter
  - 支持自动委托功能

### Changed
- **架构重构**: Hook + SubAgent 模式
  - UserPromptSubmit hook 检测关键词并创建追踪记录
  - 通过 additionalContext 引导委托 problem-tracker agent
  - Stop hook 自动记录到日期文件

### Fixed
- **stop_recorder.py**: 防止 Stop hook 无限循环
  - 检查 `stop_hook_active` 布尔值
- **数据格式统一**: 9 列表格格式
  - `| 时间戳 | 阶段 | 步骤 | 问题 | 类型 | 解决方案 | 耗时 | 优先级 | 状态 |`
- **Windows 兼容性**: Hook 命令跨平台支持
  - `py -3 ... || python3 ... || python ...`

### Removed
- 删除冗余脚本：
  - `skills/usage-observer/scripts/auto_observer.py`
  - `skills/usage-observer/scripts/record_session.py`
  - `skills/usage-observer/scripts/view_records.py`
  - `skills/usage-resolver/scripts/auto_resolver.py`

## [1.1.0] - 2026-03-02

### Added
- **自动问题追踪系统**: 全新的问题追踪架构，实现完全自动化的数据采集
  - 新增 `usage-resolver` skill: 检测解决信号，自动计算耗时
  - 新增 `state_manager.py`: 状态持久化模块，跨 Hook 调用共享数据
  - 问题检测 + 解决检测的完整追踪链
  - 无需用户确认，完全后台运行

### Changed
- **usage-observer 重构**: 从"询问式"改为"追踪式"
  - 问题出现时创建追踪记录
  - 记录开始时间和问题描述
  - 等待解决信号完成记录

### Fixed
- **用户体验优化**: 消除打断用户工作流的确认消息
  - 静默执行所有追踪操作
  - 自动计算问题解决耗时
  - 后台完成数据存储

## [1.0.2] - 2026-03-02

### Fixed
- **Windows 兼容性**: 修复 `python3` 命令在 Windows 下不存在的问题
  - Hook 命令: `python3` → `python` (marketplace.json)
  - 文档示例: `python3` → `python` (INSTALL.md, STRUCTURE.md)
  - GitHub Actions: 保持 `python3` (Linux 容器环境)
  - 脚本 shebang: 保持 `#!/usr/bin/env python3` (跨平台标准)

## [1.0.1] - 2026-02-28

### Fixed
- **Hook**: 修复 `keyword_router.py` action 类型错误
  - `type`: `"skill"` → `"invoke_skill"` (符合 Claude Code API 规范)
  - `skill`: `"usage-observer"` → `"usage-analytics:usage-observer"` (使用完整引用名)
- 修复 API Error: 400 "Request body format invalid" 错误

## [1.0.0] - 2026-02-26

### Added
- Initial release of Claude Usage Analysis Plugin
- **usage-observer**: Automatic problem detection and data collection via Hook
- **usage-recorder**: Manual detailed recording of usage issues
- **usage-analyst**: Data analysis and insight generation
- **usage-coach**: Improvement suggestions and brainstorming facilitation
- Complete role-based analytics system architecture
- Support for personal and team-level analytics
- Markdown-based data storage
- Privacy-focused local data storage

### Features

#### usage-observer
- Auto-trigger on error/problem keywords
- Extracts session stage, problem type, relevant documents
- Stores data to local markdown files
- Configurable trigger keywords

#### usage-recorder
- Manual recording with rich details
- Support for priority, status, time spent tracking
- View and query historical records
- Incremental data storage

#### usage-analyst
- Daily/weekly/monthly report generation
- Problem type distribution analysis
- Time trend analysis
- Personal and team-level insights

#### usage-coach
- GROW model-based coaching
- Brainstorming facilitation
- Training program design
- Best practices library

### Documentation
- Comprehensive README in Chinese and English
- Detailed SKILL.md for each role
- System architecture documentation
- Usage examples and workflows

[Unreleased]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.1.0
[1.0.2]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.0.2
[1.0.1]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.0.1
[1.0.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.0.0
