# 📤 纯手动上传指南（无需命令行）

如果你完全不想使用命令行，可以通过GitHub网页直接上传文件。

## 🌐 网页版上传步骤

### 1. 创建GitHub仓库
1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 仓库名输入：`MoviePilot-Plugins`
4. 描述：`MoviePilot插件集 - 包含CloudStrmAI等实用插件`
5. 选择 "Public"
6. 点击 "Create repository"

### 2. 上传插件文件

#### 上传package.json
1. 在新创建的仓库页面，点击 "uploading an existing file"
2. 拖拽或选择文件：`/tmp/MoviePilot-Plugins-dogz/package.json`
3. 提交信息：`Add package.json`
4. 点击 "Commit changes"

#### 上传package.v2.json
1. 点击 "Add file" → "Upload files"
2. 选择：`/tmp/MoviePilot-Plugins-dogz/package.v2.json`
3. 提交信息：`Add package.v2.json`
4. 点击 "Commit changes"

#### 上传README.md
1. 点击 "Add file" → "Upload files"
2. 选择：`/tmp/MoviePilot-Plugins-dogz/README.md`
3. 提交信息：`Add README.md`
4. 点击 "Commit changes"

#### 创建插件目录并上传插件文件
1. 点击 "Add file" → "Create new file"
2. 文件名输入：`plugins/CloudStrmAI/__init__.py`
3. 复制粘贴文件内容（从 `/tmp/MoviePilot-Plugins-dogz/plugins/CloudStrmAI/__init__.py`）
4. 提交信息：`Add CloudStrmAI plugin`
5. 点击 "Commit changes"

## 📋 需要复制的文件内容

### package.json 内容
```json
{
  "CloudStrmAI": {
    "name": "云盘StrmAI",
    "description": "AI智能命名的云盘Strm生成器，自动识别中英文标题提高刮削准确率。支持多季嵌套结构智能识别。",
    "labels": "云盘,Strm,AI智能命名",
    "version": "1.0.1",
    "icon": "https://raw.githubusercontent.com/thsrite/MoviePilot-Plugins/main/icons/create.png",
    "author": "dogz",
    "level": 1
  }
}
```

### package.v2.json 内容
```json
[
  {
    "id": "CloudStrmAI",
    "name": "云盘StrmAI",
    "description": "AI智能命名的云盘Strm生成器，自动识别中英文标题提高刮削准确率。支持多季嵌套结构智能识别。",
    "labels": "云盘,Strm,AI智能命名",
    "version": "1.0.1",
    "icon": "https://raw.githubusercontent.com/thsrite/MoviePilot-Plugins/main/icons/create.png",
    "author": "你的GitHub用户名",
    "author_url": "https://github.com/你的GitHub用户名",
    "repo_url": "https://github.com/你的GitHub用户名/MoviePilot-Plugins",
    "category": "工具",
    "level": 1,
    "has_page": false,
    "valid": true,
    "plugin_order": 27,
    "history": [
      {
        "version": "1.0.1",
        "date": "2024-10-03",
        "changes": "首次发布，支持AI智能命名的云盘Strm文件生成"
      }
    ]
  }
]
```

## 🔧 配置MoviePilot

上传完成后，告诉我你的GitHub用户名，我会为你生成MoviePilot配置命令。

## ✅ 成功标志

当你的GitHub仓库包含以下文件时，就成功了：
- `package.json`
- `package.v2.json`
- `README.md`
- `plugins/CloudStrmAI/__init__.py`

## 💡 提示

记得在package.v2.json中将"你的GitHub用户名"替换为实际的用户名！
