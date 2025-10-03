# CloudStrmAI 插件发布指南

## 📋 当前状态

✅ **插件文件已准备完成**
- 插件代码: `plugins/CloudStrmAI/__init__.py`
- 配置文件: `package.json` 和 `package.v2.json`
- 说明文档: `README.md`
- 自动化脚本: `deploy.sh` 和 `configure_moviepilot.sh`

## 🚀 发布步骤

### 1. 配置GitHub认证

```bash
# 使用浏览器认证（推荐）
gh auth login

# 或使用Token认证
gh auth login --with-token
```

选择以下选项：
- `GitHub.com`
- `HTTPS`
- `Yes` (authenticate with browser)

### 2. 发布插件到GitHub

```bash
cd /tmp/MoviePilot-Plugins-dogz
./deploy.sh
```

这个脚本将：
- 创建 `MoviePilot-Plugins` 仓库
- 上传所有插件文件
- 自动配置仓库信息

### 3. 配置MoviePilot加载插件

```bash
./configure_moviepilot.sh
```

这个脚本将：
- 添加你的GitHub仓库到MoviePilot插件源
- 重启MoviePilot容器
- 显示后续操作指引

## 🎯 完成后的操作

1. **等待MoviePilot启动** (约30秒)
2. **打开MoviePilot Web界面**
3. **进入插件管理**:
   - 设置 → 插件 → 插件市场
4. **搜索并安装**:
   - 搜索 "CloudStrmAI" 或 "云盘StrmAI"
   - 点击安装
5. **配置插件**:
   - 填入DeepSeek API Key
   - 配置监控目录
   - 启用插件

## 📊 插件特性

- ✨ **AI智能命名**: DeepSeek API驱动
- 🎯 **高精度识别**: 中英文标题提取
- 📁 **多格式支持**: 电影/电视剧标准化
- 🔄 **云盘集成**: Alist/CD2支持
- 📊 **嵌套处理**: 多季目录结构

## 🔧 故障排除

### 插件不显示
1. 检查GitHub仓库是否公开
2. 确认package.json格式正确
3. 重启MoviePilot容器
4. 查看MoviePilot日志

### 安装失败
1. 检查插件代码语法
2. 确认依赖库已安装
3. 查看详细错误日志

## 📞 支持

如有问题，请：
1. 查看MoviePilot日志
2. 检查GitHub仓库设置
3. 在GitHub Issues中反馈

## 🎉 成功标志

当你在MoviePilot插件市场中看到 "云盘StrmAI" 插件时，说明发布成功！
