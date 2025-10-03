#!/bin/bash

echo "🔧 为 dogzong 配置 MoviePilot 加载 CloudStrmAI 插件..."
echo ""

REPO_URL="https://github.com/dogzong/MoviePilot-Plugins"
DB_PATH="/home/dogz/docker/moviepilot/config/user.db"

echo "📝 仓库地址: $REPO_URL"
echo "💾 数据库路径: $DB_PATH"
echo ""

# 检查数据库文件
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 找不到MoviePilot数据库文件: $DB_PATH"
    echo "请确认MoviePilot已正确安装并运行"
    exit 1
fi

echo "💾 备份数据库..."
cp "$DB_PATH" "${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ 数据库已备份"

echo ""
echo "📊 添加插件仓库到MoviePilot配置..."

# 使用Python处理JSON配置
python3 << 'EOF'
import json
import sqlite3
import sys

DB_PATH = '/home/dogz/docker/moviepilot/config/user.db'
REPO_URL = 'https://github.com/dogzong/MoviePilot-Plugins'

try:
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取现有插件仓库配置
    cursor.execute("SELECT value FROM systemconfig WHERE key = 'PLUGIN_REPOS'")
    result = cursor.fetchone()
    
    if result:
        current_repos_str = result[0]
        try:
            current_repos = json.loads(current_repos_str)
        except:
            current_repos = []
    else:
        current_repos = []
    
    # 添加新仓库（如果不存在）
    if REPO_URL not in current_repos:
        current_repos.append(REPO_URL)
        print(f"✅ 已添加插件仓库: {REPO_URL}")
        
        # 更新数据库
        if result:
            cursor.execute("UPDATE systemconfig SET value = ? WHERE key = 'PLUGIN_REPOS'", (json.dumps(current_repos),))
        else:
            cursor.execute("INSERT INTO systemconfig (key, value) VALUES ('PLUGIN_REPOS', ?)", (json.dumps(current_repos),))
        
        conn.commit()
        print("💾 数据库配置已更新")
    else:
        print(f"ℹ️  插件仓库已存在: {REPO_URL}")
    
    print("\n📊 当前插件仓库列表:")
    for i, repo in enumerate(current_repos, 1):
        print(f"  {i}. {repo}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 配置失败: {e}")
    sys.exit(1)

print("\n✅ 插件仓库配置成功!")
EOF

# 检查Python脚本执行结果
if [ $? -ne 0 ]; then
    echo "❌ 配置插件仓库失败"
    exit 1
fi

echo ""
echo "🔄 重启MoviePilot容器以加载新配置..."
docker restart moviepilot

echo ""
echo "⏳ 等待MoviePilot启动 (30秒)..."
sleep 30

echo ""
echo "🎉 配置完成！"
echo ""
echo "🌟 CloudStrmAI插件已准备就绪"
echo ""
echo "🎯 后续操作步骤:"
echo "1. 📱 打开MoviePilot Web界面: http://localhost:3000"
echo "2. 🔧 进入: 设置 → 插件 → 插件市场"
echo "3. 🔄 点击刷新插件市场"
echo "4. 🔍 搜索: 'CloudStrmAI' 或 '云盘StrmAI'"
echo "5. ⬇️  点击安装插件"
echo "6. ⚙️  配置插件:"
echo "   - 填入 DeepSeek API Key"
echo "   - 设置监控目录"
echo "   - 启用AI智能命名"
echo ""
echo "📋 插件仓库地址:"
echo "   https://github.com/dogzong/MoviePilot-Plugins"
echo ""
echo "✨ CloudStrmAI特性:"
echo "   - 🤖 AI智能命名 (DeepSeek API驱动)"
echo "   - 🎯 高精度中英文标题提取"
echo "   - 📁 电影/电视剧标准化命名"
echo "   - 🔄 多云盘支持 (Alist/CD2)"
echo "   - 📊 智能嵌套目录处理"
echo ""
echo "🆘 如有问题:"
echo "   - 查看MoviePilot日志"
echo "   - 检查插件仓库是否可访问"
echo "   - 在GitHub仓库提交Issues"
