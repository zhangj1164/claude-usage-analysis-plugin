# Pre-Publish Checklist

## ✅ GitHub Repository Setup

### 1. Create Repository on GitHub

- [ ] Go to https://github.com/new
- [ ] Repository name: `claude-usage-analysis-plugin`
- [ ] Description: `Claude Code usage analytics system - automatic collection, analysis, and improvement suggestions`
- [ ] Visibility: **Public** (recommended for sharing)
- [ ] **DO NOT** initialize with README, .gitignore, or License (we have them already)
- [ ] Click "Create repository"

### 2. Initialize and Push

```bash
# Navigate to plugin directory
cd C:\Users\zjlzld\Documents\trae_projects\plugins\claude-usage-analysis-plugin

# Make init script executable (Unix/Mac)
chmod +x init-git.sh

# Run initialization script
./init-git.sh your-github-username

# Or manually:
git init
git add .
git commit -m "Initial commit: Claude Usage Analysis Plugin v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/claude-usage-analysis-plugin.git
git push -u origin main
```

### 3. Create Release

```bash
# Create version tag
git tag -a v1.0.0 -m "Release v1.0.0

Features:
- Automatic problem detection via Hook
- Manual detailed recording
- Data analysis and reporting
- Improvement coaching

Complete role-based analytics system for Claude Code."

# Push tag
git push origin v1.0.0
```

## ✅ GitHub Repository Settings

### Settings → General

- [ ] **Topics**: Add these topics
  - `claude-code`
  - `claude-plugin`
  - `agent-skills`
  - `analytics`
  - `productivity`
  - `team-tools`

- [ ] **Social Preview**: Upload an image (optional)
  - Recommended size: 1280×640px

### Settings → Actions → General

- [ ] **Actions permissions**: Select "Allow all actions and reusable workflows"
- [ ] **Workflow permissions**: Select "Read and write permissions"

## ✅ Files Verification

### Required Files (Claude Code Plugin Spec)

- [x] `marketplace.json` - Plugin manifest
- [x] `README.md` - Main documentation
- [x] `LICENSE` - MIT License

### Documentation Files

- [x] `INSTALL.md` - Installation guide
- [x] `EXAMPLES.md` - Usage examples
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `CHANGELOG.md` - Version history
- [x] `STRUCTURE.md` - Project structure
- [x] `CHECKLIST.md` - This file

### CI/CD Files

- [x] `.github/workflows/ci.yml` - CI validation
- [x] `.github/workflows/release.yml` - Release automation

### Skills

- [x] `skills/usage-observer/SKILL.md`
- [x] `skills/usage-observer/LICENSE.txt`
- [x] `skills/usage-recorder/SKILL.md`
- [x] `skills/usage-recorder/LICENSE.txt`
- [x] `skills/usage-analyst/SKILL.md`
- [x] `skills/usage-analyst/LICENSE.txt`
- [x] `skills/usage-coach/SKILL.md`
- [x] `skills/usage-coach/LICENSE.txt`

## ✅ Content Validation

### marketplace.json

- [ ] `name` matches repository name
- [ ] `description` is clear and concise
- [ ] `plugins[0].skills` lists all skill paths correctly

### SKILL.md Files

Each skill should have:
- [ ] YAML frontmatter with `name` field
- [ ] YAML frontmatter with `description` field
- [ ] Clear trigger conditions in description
- [ ] Usage instructions
- [ ] Examples

## ✅ Testing

### Local Testing

```bash
# Install locally
claude plugin add C:\Users\zjlzld\Documents\trae_projects\plugins\claude-usage-analysis-plugin

# Verify installation
claude plugin list

# Test each skill
```

### Test Scenarios

- [ ] `usage-observer`: Say "我遇到了错误" should trigger
- [ ] `usage-recorder`: Say "记录这个问题" should trigger
- [ ] `usage-analyst`: Say "分析使用情况" should trigger
- [ ] `usage-coach`: Say "给我一些建议" should trigger

## ✅ Post-Publish

### Documentation

- [ ] Update README with actual GitHub username
- [ ] Update marketplace.json owner email if desired
- [ ] Update installation URLs in README and INSTALL.md

### Sharing

- [ ] Share on Twitter/X
- [ ] Post in Claude Code community
- [ ] Share with your team

### Maintenance

- [ ] Set up issue templates (optional)
- [ ] Enable discussions (optional)
- [ ] Add repository to watchlist

## 🚀 Quick Start for Users

After publishing, users can install with:

```bash
# Install from GitHub
claude plugin add https://github.com/YOUR_USERNAME/claude-usage-analysis-plugin

# Or specific version
claude plugin add https://github.com/YOUR_USERNAME/claude-usage-analysis-plugin@v1.0.0
```

Then configure Hook in `~/.claude/config.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "skills": ["usage-observer"],
      "trigger_keywords": [
        "错误", "失败", "问题", "报错",
        "error", "exception", "bug", "failed"
      ]
    }
  }
}
```

## 📞 Support

- **Issues**: https://github.com/YOUR_USERNAME/claude-usage-analysis-plugin/issues
- **Documentation**: See README.md

---

**Ready to publish!** 🎉

Remember to replace `YOUR_USERNAME` with your actual GitHub username in all URLs.
