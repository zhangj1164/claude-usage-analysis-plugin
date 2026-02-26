# Installation Guide

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 中文安装指南

### 系统要求

- Claude Code CLI 已安装
- Python 3.7+（用于脚本功能）
- Git（用于从 GitHub 安装）

### 安装方式

#### 方式 1：从 GitHub 安装（推荐）

```bash
claude plugin add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

#### 方式 2：从本地目录安装

1. 克隆或下载插件：
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
cd claude-usage-analysis-plugin
```

2. 安装插件：
```bash
claude plugin add .
```

#### 方式 3：从 Release 包安装

1. 从 [Releases](../../releases) 页面下载最新版本
2. 解压到本地目录
3. 安装：
```bash
claude plugin add /path/to/claude-usage-analysis-plugin
```

### 配置步骤

#### 步骤 1：验证安装

安装完成后，验证插件是否生效：

```bash
claude plugin list
```

应该能看到 `claude-usage-analysis-plugin` 及其包含的 skills：
- `usage-observer`
- `usage-recorder`
- `usage-analyst`
- `usage-coach`

#### 步骤 2：配置自动采集 Hook

编辑你的 Claude Code 配置文件（通常在 `~/.claude/config.json`）：

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "错误", "失败", "问题", "报错",
        "error", "exception", "bug", "failed",
        "不对", "错了", "有问题", "crash", "timeout",
        "失败", "无法", "不能"
      ]
    }
  }
}
```

**Windows 配置路径**：
- 配置文件位置：`%USERPROFILE%\.claude\config.json`

**Mac/Linux 配置路径**：
- 配置文件位置：`~/.claude/config.json`

#### 步骤 3：测试配置

1. **测试自动采集**：
   - 开始一个新的 Claude Code 会话
   - 输入包含"错误"的句子，如："运行命令报错了"
   - 应该看到 observer 自动触发

2. **测试手动记录**：
   - 说："记录这个问题"
   - Claude 应该询问详细信息

3. **测试数据分析**：
   - 说："分析今天的使用情况"
   - Claude 应该生成分析报告

### 团队部署

#### 为团队成员统一配置

1. **创建团队配置文件模板**：

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "错误", "失败", "问题", "报错",
        "error", "exception", "bug", "failed",
        "不对", "错了", "有问题"
      ]
    }
  },
  "plugins": {
    "claude-usage-analysis-plugin": {
      "enabled": true
    }
  }
}
```

2. **分发配置**：
   - 将配置放在团队共享位置
   - 成员复制到各自的配置目录

3. **验证部署**：
   - 收集成员反馈
   - 调整关键词和配置

### 故障排除

#### 问题：Hook 没有触发

**检查项**：
1. 插件是否正确安装：`claude plugin list`
2. 配置文件位置是否正确
3. JSON 格式是否有效

**解决**：
```bash
# 验证配置文件格式
python3 -m json.tool ~/.claude/config.json
```

#### 问题：数据没有保存

**检查项**：
1. 检查存储目录权限
2. 查看是否有错误日志

**解决**：
```bash
# 检查存储目录
ls -la ~/.claude/claude-analysis/

# 手动创建目录
mkdir -p ~/.claude/claude-analysis
```

#### 问题：Skill 未激活

**检查项**：
1. 描述是否清晰准确
2. 是否与需求匹配

**解决**：
- 查看 SKILL.md 中的触发条件
- 确保表达符合触发描述

### 更新插件

```bash
# 从 GitHub 更新
claude plugin update claude-usage-analysis-plugin

# 或重新安装
claude plugin remove claude-usage-analysis-plugin
claude plugin add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

### 卸载

```bash
claude plugin remove claude-usage-analysis-plugin
```

---

<a name="english"></a>
## English Installation Guide

### System Requirements

- Claude Code CLI installed
- Python 3.7+ (for script functionality)
- Git (for GitHub installation)

### Installation Methods

#### Option 1: Install from GitHub (Recommended)

```bash
claude plugin add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

#### Option 2: Install from Local Directory

1. Clone or download the plugin:
```bash
git clone https://github.com/zhangj1164/claude-usage-analysis-plugin.git
cd claude-usage-analysis-plugin
```

2. Install the plugin:
```bash
claude plugin add .
```

#### Option 3: Install from Release Package

1. Download the latest release from [Releases](../../releases)
2. Extract to a local directory
3. Install:
```bash
claude plugin add /path/to/claude-usage-analysis-plugin
```

### Configuration

#### Step 1: Verify Installation

After installation, verify the plugin is active:

```bash
claude plugin list
```

You should see `claude-usage-analysis-plugin` and its skills:
- `usage-observer`
- `usage-recorder`
- `usage-analyst`
- `usage-coach`

#### Step 2: Configure Auto-Collection Hook

Edit your Claude Code configuration file (usually at `~/.claude/config.json`):

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

**Windows Config Path**: `%USERPROFILE%\.claude\config.json`

**Mac/Linux Config Path**: `~/.claude/config.json`

#### Step 3: Test Configuration

1. **Test Auto-Collection**:
   - Start a new Claude Code session
   - Type something with "error", like: "I got an error"
   - The observer should auto-trigger

2. **Test Manual Recording**:
   - Say: "record this issue"
   - Claude should ask for details

3. **Test Data Analysis**:
   - Say: "analyze my usage today"
   - Claude should generate a report

### Team Deployment

#### Uniform Configuration for Team Members

1. **Create team config template**:

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "error", "exception", "bug", "failed",
        "wrong", "issue", "crash", "timeout"
      ]
    }
  },
  "plugins": {
    "claude-usage-analysis-plugin": {
      "enabled": true
    }
  }
}
```

2. **Distribute configuration**:
   - Place config in team shared location
   - Members copy to their config directories

3. **Verify deployment**:
   - Collect member feedback
   - Adjust keywords and configuration

### Troubleshooting

#### Issue: Hook not triggering

**Check**:
1. Plugin installed correctly: `claude plugin list`
2. Config file in correct location
3. JSON format is valid

**Fix**:
```bash
# Validate config file format
python3 -m json.tool ~/.claude/config.json
```

#### Issue: Data not saving

**Check**:
1. Storage directory permissions
2. Error logs

**Fix**:
```bash
# Check storage directory
ls -la ~/.claude/claude-analysis/

# Create directory manually
mkdir -p ~/.claude/claude-analysis
```

#### Issue: Skill not activating

**Check**:
1. Description is clear and accurate
2. Matches your request

**Fix**:
- Review trigger conditions in SKILL.md
- Ensure your expression matches the description

### Updating

```bash
# Update from GitHub
claude plugin update claude-usage-analysis-plugin

# Or reinstall
claude plugin remove claude-usage-analysis-plugin
claude plugin add https://github.com/zhangj1164/claude-usage-analysis-plugin
```

### Uninstall

```bash
claude plugin remove claude-usage-analysis-plugin
```

---

## Getting Help

- [Open an Issue](../../issues)
- [View Documentation](README.md)
- [Contribution Guide](CONTRIBUTING.md)
