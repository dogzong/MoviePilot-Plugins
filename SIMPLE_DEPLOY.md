# 🚀 超简单发布指南（5分钟搞定）

## 方案A：使用GitHub Token（推荐）

### 1. 获取GitHub Token
1. 打开 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写 Token 名称：`MoviePilot Plugin`
4. 选择过期时间：`30 days`
5. 勾选权限：`repo` (完整的仓库权限)
6. 点击 "Generate token"
7. **复制生成的Token**（只显示一次）

### 2. 运行发布命令
```bash
# 输入你的Token进行认证
echo "你的GitHub_Token" | gh auth login --with-token

# 一键发布
cd /tmp/MoviePilot-Plugins-dogz
./deploy.sh

# 配置MoviePilot
./configure_moviepilot.sh
```

---

## 方案B：手动创建仓库（最简单）

如果上面的方法还是太复杂，我可以帮你手动创建：

### 1. 在GitHub网页上创建仓库
1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名：`MoviePilot-Plugins`
4. 设置为 Public
5. 点击 "Create repository"

### 2. 我帮你准备上传命令
告诉我你的GitHub用户名，我就能为你生成具体的上传命令。

---

## 方案C：我帮你逐步操作

如果你愿意，我们可以一步一步来：

1. **你只需要**：创建GitHub仓库（网页操作）
2. **我来做**：生成所有上传和配置命令
3. **你只需要**：复制粘贴运行命令

这样你只需要做最少的操作，其余都由我来处理！

---

## 🛡️ 安全提醒

**绝对不要**在任何地方分享你的：
- GitHub密码
- 个人访问令牌
- SSH私钥

正确的做法是使用上述安全方法进行认证。

---

## 💭 选择哪种方案？

告诉我你想用哪种方案，我立即为你提供详细的操作指导！
