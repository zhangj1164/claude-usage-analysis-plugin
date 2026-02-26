#!/bin/bash
# GitHub Repository Initialization Script
# Usage: ./init-git.sh <your-github-username>

set -e

USERNAME=${1:-"your-username"}
REPO_NAME="claude-usage-analysis-plugin"

if [ "$USERNAME" = "your-username" ]; then
    echo "❌ Please provide your GitHub username"
    echo "Usage: ./init-git.sh your-github-username"
    exit 1
fi

echo "🚀 Initializing GitHub repository for $USERNAME/$REPO_NAME"
echo ""

# Check if git is initialized
if [ -d ".git" ]; then
    echo "⚠️  Git already initialized"
else
    echo "📦 Initializing git..."
    git init
    git branch -M main
fi

# Add all files
echo "📁 Adding files..."
git add .

# Initial commit
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "⚠️  Commit already exists"
else
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: Claude Usage Analysis Plugin v1.0.0

- Add usage-observer: automatic problem detection
- Add usage-recorder: manual detailed recording
- Add usage-analyst: data analysis and reporting
- Add usage-coach: improvement suggestions
- Complete role-based analytics system
- Bilingual documentation (CN/EN)"
fi

# Add remote
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  Remote already exists"
else
    echo "🔗 Adding remote..."
    git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
fi

echo ""
echo "✅ Git initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create repository on GitHub: https://github.com/new"
echo "   Name: $REPO_NAME"
echo "   Visibility: Public (recommended)"
echo ""
echo "2. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "3. Create a release:"
echo "   git tag -a v1.0.0 -m 'Release v1.0.0'"
echo "   git push origin v1.0.0"
echo ""
echo "4. Install in Claude Code:"
echo "   claude plugin install https://github.com/$USERNAME/$REPO_NAME"
echo ""
