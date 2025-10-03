#!/bin/bash

echo "🚀 为 dogzong 发布 CloudStrmAI 插件到 GitHub..."
echo ""

# 检查GitHub CLI认证状态
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI未认证"
    echo ""
    echo "请选择认证方式："
    echo "1️⃣  浏览器认证（推荐）："
    echo "   gh auth login"
    echo ""
    echo "2️⃣  Token认证："
    echo "   获取Token: https://github.com/settings/tokens"
    echo "   然后运行: echo '你的Token' | gh auth login --with-token"
    echo ""
    exit 1
fi

# 获取当前用户名确认
GITHUB_USER=$(gh api user --jq '.login')
if [ "$GITHUB_USER" != "dogzong" ]; then
    echo "⚠️  检测到GitHub用户名为: $GITHUB_USER"
    echo "⚠️  但脚本配置为: dogzong"
    echo ""
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 操作已取消"
        exit 1
    fi
else
    echo "✅ GitHub用户确认: $GITHUB_USER"
fi

# 初始化Git仓库
echo ""
echo "📝 初始化Git仓库..."
git init
echo "node_modules/" > .gitignore
echo "*.log" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 添加所有文件
echo "📦 添加文件..."
git add .
git commit -m "🎉 Initial commit: CloudStrmAI v1.0.1

✨ AI智能命名的云盘Strm生成器

主要特性:
- 🤖 DeepSeek API智能分析文件名
- 🎯 自动提取中英文标题、年份、季集信息
- 📁 支持电影和电视剧标准化命名
- 🔄 支持Alist、CD2等多种云盘挂载
- 📊 智能处理多季嵌套目录结构

作者: dogzong
版本: 1.0.1
日期: $(date +%Y-%m-%d)"

# 检查仓库是否已存在
echo ""
echo "🔍 检查仓库状态..."
if gh repo view dogzong/MoviePilot-Plugins >/dev/null 2>&1; then
    echo "📦 仓库已存在，准备更新..."
    git branch -M main
    git remote add origin "https://github.com/dogzong/MoviePilot-Plugins.git"
    
    # 强制推送更新
    echo "⬆️  推送更新到GitHub..."
    git push -f origin main
else
    # 创建新仓库
    echo "📦 创建新的GitHub仓库..."
    gh repo create MoviePilot-Plugins --public --description "MoviePilot插件集 - 包含CloudStrmAI等实用插件，支持AI智能命名" --clone=false
    
    # 推送代码
    git branch -M main
    git remote add origin "https://github.com/dogzong/MoviePilot-Plugins.git"
    echo "⬆️  推送到GitHub..."
    git push -u origin main
fi

echo ""
echo "🎉 插件发布成功！"
echo ""
echo "🔗 仓库地址:"
echo "   https://github.com/dogzong/MoviePilot-Plugins"
echo ""
echo "📋 插件市场地址 (用于MoviePilot配置):"
echo "   https://github.com/dogzong/MoviePilot-Plugins"
echo ""
echo "🎯 下一步:"
echo "   运行: ./configure_dogzong.sh"
echo "   或手动在MoviePilot中添加插件源"
echo ""
echo "✨ CloudStrmAI插件特性:"
echo "   - AI智能命名 (DeepSeek API)"
echo "   - 中英文标题识别"
echo "   - 多云盘支持 (Alist/CD2)"
echo "   - 嵌套目录智能处理"
