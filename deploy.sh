#!/bin/bash

echo "🚀 开始发布CloudStrmAI插件到GitHub..."

# 检查GitHub CLI认证状态
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI未认证，请先运行: gh auth login"
    exit 1
fi

# 获取当前用户名
GITHUB_USER=$(gh api user --jq '.login')
echo "📝 GitHub用户: $GITHUB_USER"

# 更新配置文件中的用户名
sed -i "s/dogz/$GITHUB_USER/g" package.v2.json
sed -i "s/dogz/$GITHUB_USER/g" README.md

# 初始化Git仓库
git init
echo "node_modules/" > .gitignore
echo "*.log" >> .gitignore
echo ".DS_Store" >> .gitignore

# 添加所有文件
git add .
git commit -m "🎉 Initial commit: Add CloudStrmAI plugin v1.0.1

✨ Features:
- AI-powered intelligent naming using DeepSeek API
- Support for movies and TV shows
- Multiple cloud storage integration (Alist, CD2)
- Smart nested directory structure recognition
- Chinese and English title extraction
- Season and episode detection"

# 创建GitHub仓库
echo "📦 创建GitHub仓库..."
gh repo create MoviePilot-Plugins --public --description "MoviePilot插件集 - 包含CloudStrmAI等实用插件" --clone=false

# 添加远程仓库并推送
git branch -M main
git remote add origin "https://github.com/$GITHUB_USER/MoviePilot-Plugins.git"
git push -u origin main

echo "✅ 插件发布成功！"
echo ""
echo "🔗 仓库地址: https://github.com/$GITHUB_USER/MoviePilot-Plugins"
echo ""
echo "📋 在MoviePilot中添加插件源:"
echo "https://github.com/$GITHUB_USER/MoviePilot-Plugins"
echo ""
echo "🎯 下一步操作:"
echo "1. 在MoviePilot设置 -> 插件 -> 插件仓库中添加上述地址"
echo "2. 刷新插件市场"
echo "3. 搜索并安装CloudStrmAI插件"
