# 🎯 dogzong 专属 CloudStrmAI 插件发布指南

## 📋 准备就绪

✅ **用户信息已配置**
- GitHub用户名: `dogzong`
- 邮箱: `chom2733@gmail.com`
- 仓库地址: `https://github.com/dogzong/MoviePilot-Plugins`

✅ **所有文件已准备**
- 插件代码: `plugins/CloudStrmAI/__init__.py`
- 配置文件: `package.json` & `package.v2.json`
- 说明文档: `README.md`
- 专属脚本: `deploy_dogzong.sh` & `configure_dogzong.sh`

## 🚀 发布步骤（超级简单）

### 步骤1: GitHub认证 (2分钟)

选择一种认证方式：

#### 方法A: 浏览器认证（推荐）
```bash
gh auth login
```
然后选择：
- `GitHub.com`
- `HTTPS` 
- `Yes` (authenticate with browser)

#### 方法B: Token认证
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 名称填: `MoviePilot Plugin`
4. 勾选: `repo` (完整仓库权限)
5. 点击 "Generate token" 
6. 复制Token，运行:
```bash
echo '你的Token' | gh auth login --with-token
```

### 步骤2: 一键发布 (1分钟)
```bash
cd /tmp/MoviePilot-Plugins-dogz
./deploy_dogzong.sh
```

### 步骤3: 配置MoviePilot (1分钟)
```bash
./configure_dogzong.sh
```

## 🎉 完成后你将获得

- 🔗 **GitHub仓库**: https://github.com/dogzong/MoviePilot-Plugins
- 📦 **插件源地址**: 自动添加到MoviePilot
- ✨ **插件显示**: CloudStrmAI将在插件市场显示
- 🎊 **功能齐全**: AI智能命名、多云盘支持等

## 🎯 最后步骤 (Web界面操作)

1. **打开MoviePilot**: http://localhost:3000
2. **进入插件管理**: 设置 → 插件 → 插件市场
3. **刷新插件市场**: 点击刷新按钮
4. **搜索插件**: 输入 "CloudStrmAI" 或 "云盘StrmAI"
5. **安装插件**: 点击安装
6. **配置插件**:
   - DeepSeek API Key: 从 https://platform.deepseek.com 获取
   - 监控目录: 按格式配置
   - 启用AI智能命名

## 📊 CloudStrmAI插件特性

- 🤖 **AI智能命名**: DeepSeek API驱动的智能分析
- 🎯 **高精度识别**: 自动提取中英文标题、年份、季集信息
- 📁 **标准化命名**: 支持电影和电视剧的MoviePilot标准格式
- 🔄 **多云盘支持**: Alist、CD2等多种挂载方式
- 📊 **嵌套处理**: 智能识别多季嵌套目录结构
- ⚡ **高效处理**: 缓存机制避免重复API调用

## 🔧 监控目录配置格式

### 基础格式
```
/dav/quark/tv-nastool#/downloads/complete/tv#/media/tv
```

### Alist格式  
```
/dav/quark/tv#/downloads/complete/tv#alist#/dav#dogz:558855@192.168.31.154:19039
```

### CD2格式
```
/dav/quark/tv#/downloads/complete/tv#cd2#/dav#服务地址
```

## 🆘 故障排除

### 插件不显示
1. 确认GitHub仓库已创建且为公开
2. 检查package.json格式是否正确
3. 重启MoviePilot容器: `docker restart moviepilot`
4. 查看日志: `docker logs moviepilot`

### 认证失败
1. 重新运行: `gh auth login`
2. 确认GitHub账号为: dogzong
3. 检查网络连接

### 插件安装失败
1. 检查插件代码语法
2. 查看MoviePilot详细日志
3. 确认依赖库已安装

## 📞 获得帮助

- 🔗 GitHub仓库: https://github.com/dogzong/MoviePilot-Plugins
- 📧 提交Issues获得支持
- 📊 查看MoviePilot日志排查问题

## 🎊 成功标志

当你在MoviePilot插件市场看到 **"云盘StrmAI"** 插件并能正常安装时，说明发布完全成功！

---

**准备好了吗？只需运行3个命令就能完成发布！🚀**
