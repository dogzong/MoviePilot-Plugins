#!/bin/bash

echo "🔧 配置MoviePilot加载CloudStrmAI插件..."

# 获取GitHub用户名
if gh auth status >/dev/null 2>&1; then
    GITHUB_USER=$(gh api user --jq '.login')
    REPO_URL="https://github.com/$GITHUB_USER/MoviePilot-Plugins"
else
    echo "请输入你的GitHub用户名:"
    read GITHUB_USER
    REPO_URL="https://github.com/$GITHUB_USER/MoviePilot-Plugins"
fi

echo "📝 仓库地址: $REPO_URL"

# 检查数据库
DB_PATH="/home/dogz/docker/moviepilot/config/user.db"

if [ ! -f "$DB_PATH" ]; then
    echo "❌ 找不到MoviePilot数据库文件: $DB_PATH"
    exit 1
fi

echo "💾 添加插件仓库到MoviePilot配置..."

# 获取现有插件仓库配置
CURRENT_REPOS=$(sqlite3 "$DB_PATH" "SELECT value FROM systemconfig WHERE key = 'PLUGIN_REPOS';" 2>/dev/null || echo "[]")

# 如果配置不存在，创建新配置
if [ "$CURRENT_REPOS" = "" ]; then
    CURRENT_REPOS="[]"
fi

# 使用Python处理JSON
python3 << EOF
import json
import sqlite3

# 读取现有配置
current_repos_str = '''$CURRENT_REPOS'''
try:
    if current_repos_str.strip() == '':
        current_repos = []
    else:
        current_repos = json.loads(current_repos_str)
except:
    current_repos = []

# 添加新仓库（如果不存在）
new_repo = "$REPO_URL"
if new_repo not in current_repos:
    current_repos.append(new_repo)
    print(f"✅ 已添加插件仓库: {new_repo}")
else:
    print(f"ℹ️  插件仓库已存在: {new_repo}")

# 更新数据库
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()

# 检查配置是否存在
cursor.execute("SELECT COUNT(*) FROM systemconfig WHERE key = 'PLUGIN_REPOS'")
exists = cursor.fetchone()[0]

if exists > 0:
    cursor.execute("UPDATE systemconfig SET value = ? WHERE key = 'PLUGIN_REPOS'", (json.dumps(current_repos),))
else:
    cursor.execute("INSERT INTO systemconfig (key, value) VALUES ('PLUGIN_REPOS', ?)", (json.dumps(current_repos),))

conn.commit()
conn.close()

print("📊 当前插件仓库列表:")
for i, repo in enumerate(current_repos, 1):
    print(f"  {i}. {repo}")
EOF

echo ""
echo "🔄 重启MoviePilot容器以加载新配置..."
docker restart moviepilot

echo ""
echo "✅ 配置完成！"
echo ""
echo "🎯 后续步骤:"
echo "1. 等待MoviePilot完全启动（约30秒）"
echo "2. 打开MoviePilot Web界面"
echo "3. 进入 设置 -> 插件 -> 插件市场"
echo "4. 搜索 'CloudStrmAI' 或 '云盘StrmAI'"
echo "5. 点击安装插件"
echo ""
echo "📋 插件仓库地址: $REPO_URL"
