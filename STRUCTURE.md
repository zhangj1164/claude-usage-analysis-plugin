# Project Structure

```
claude-usage-analysis-plugin/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI checks (validation, lint, docs)
│       └── release.yml         # Automatic release workflow
│
├── assets/
│   └── icon.svg                # Plugin icon
│
├── skills/
│   ├── usage-observer/         # 👁️ Automatic problem detection
│   │   ├── LICENSE.txt
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── record_session.py
│   │       └── view_records.py
│   │
│   ├── usage-recorder/         # 📝 Manual detailed recording
│   │   ├── LICENSE.txt
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── record_session.py
│   │       └── view_records.py
│   │
│   ├── usage-analyst/          # 📊 Data analysis & reporting
│   │   ├── LICENSE.txt
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── analyze_usage.py
│   │
│   └── usage-coach/            # 🎯 Improvement coaching
│       ├── LICENSE.txt
│       ├── SKILL.md
│       └── references/
│           └── best-practices.md
│
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version changelog
├── CONTRIBUTING.md             # Contribution guidelines
├── EXAMPLES.md                 # Usage examples (中文/English)
├── INSTALL.md                  # Installation guide (中文/English)
├── LICENSE                     # MIT License
├── marketplace.json            # Plugin manifest (entry point)
├── README.md                   # Main documentation (中文/English)
└── STRUCTURE.md                # This file
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `marketplace.json` | **Required** - Plugin manifest, defines plugin metadata and skills |
| `README.md` | **Required** - Main documentation with usage instructions |
| `LICENSE` | **Required** - MIT License |
| `.gitignore` | Git ignore patterns |

### Documentation

| File | Purpose |
|------|---------|
| `INSTALL.md` | Detailed installation guide (bilingual) |
| `EXAMPLES.md` | Usage examples and scenarios (bilingual) |
| `CONTRIBUTING.md` | How to contribute to the project |
| `CHANGELOG.md` | Version history and changes |
| `STRUCTURE.md` | This file - project structure reference |

### GitHub Integration

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | CI pipeline - validates skills, lints code |
| `.github/workflows/release.yml` | Release automation - creates releases on git tags |

### Skills

Each skill follows the Agent Skills specification:

```
skills/{skill-name}/
├── SKILL.md          # Required - Skill definition and instructions
├── LICENSE.txt       # License file
└── scripts/          # Optional - Executable scripts
└── references/       # Optional - Reference materials
└── assets/           # Optional - Templates, images
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User/Team Member                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌────────────────┐
│ Auto Detect  │      │ Manual Record  │
│ (Observer)   │      │ (Recorder)     │
│              │      │  - 直接调用     │
│ 检测问题关键词 │      │  - 交互式记录   │
│ 分析会话内容  │      │                │
└──────┬───────┘      └───────┬────────┘
       │                       │
       │ 调用 recorder          │
       ▼                       │
┌──────────────┐               │
│   Record     │◄──────────────┘
│ (Recorder)   │   统一数据存储入口
│              │
│ 写入文件      │
│ 更新统计      │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│   Data Storage       │
│ ~/.claude/claude-analysis/
└──────────┬──────────┘
           │
       ┌───┴───┐
       │       │
       ▼       ▼
┌──────────┐ ┌──────────────┐
│  Analyst │ │ Coach & Guide│
│  数据分析 │ │   改进教练    │
└──────────┘ └──────────────┘
```

### Skill 调用关系

```
Hook (UserPromptSubmit)
    │
    ▼
usage-observer (自动检测分析)
    │
    │ skill:usage-recorder
    ▼
usage-recorder (数据存储)
    │
    ▼
Markdown 文件
```

**说明**:
- `usage-observer` 只负责检测和分析，不直接存储数据
- `usage-recorder` 是唯一的存储入口，可被 observer 调用或用户直接调用
- 这种设计保证了存储逻辑的一致性和可维护性

## GitHub Repository Setup

### Required for Publishing

1. **Create Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/username/claude-usage-analysis-plugin.git
   git push -u origin main
   ```

2. **Add Topics** (in GitHub repo settings)
   - `claude-code`
   - `claude-plugin`
   - `agent-skills`
   - `analytics`
   - `productivity`

3. **Enable Actions** (in GitHub repo settings)
   - Actions → General → Allow all actions

4. **Create Release**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Installation URLs

After publishing to GitHub, users can install via:

```bash
# Git URL
claude plugin install https://github.com/username/claude-usage-analysis-plugin

# Specific version
claude plugin install https://github.com/username/claude-usage-analysis-plugin@v1.0.0
```

## Development

### Local Testing

```bash
# Clone repository
git clone https://github.com/username/claude-usage-analysis-plugin.git
cd claude-usage-analysis-plugin

# Install locally
claude plugin install .

# Test changes
claude plugin update claude-usage-analysis-plugin
```

### Validation

```bash
# Validate marketplace.json
python -c "import json; json.load(open('marketplace.json'))"

# Check skill structure
python -c "
import json
import os

with open('marketplace.json') as f:
    data = json.load(f)

for plugin in data['plugins']:
    for skill in plugin['skills']:
        skill_path = skill.replace('./', '')
        assert os.path.exists(f'{skill_path}/SKILL.md'), f'Missing {skill_path}/SKILL.md'
        print(f'✓ {skill_path}')
"
```
