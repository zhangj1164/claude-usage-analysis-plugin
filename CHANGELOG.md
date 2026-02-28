# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/zhangj1164/claude-usage-analysis-plugin/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.0.1
[1.0.0]: https://github.com/zhangj1164/claude-usage-analysis-plugin/releases/tag/v1.0.0
