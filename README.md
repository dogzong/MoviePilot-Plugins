# MoviePilot 插件集

这是 dogzong 的 MoviePilot 插件仓库。

## 插件列表

### CloudStrmAI - 云盘StrmAI

**版本**: 1.0.1  
**作者**: dogzong
**分类**: 工具  

#### 功能描述

AI智能命名的云盘Strm生成器，自动识别中英文标题提高刮削准确率。支持多季嵌套结构智能识别。

#### 主要特性

- ✨ **AI智能命名**: 使用DeepSeek API智能分析文件夹和文件名
- 🎯 **高精度识别**: 自动提取中英文标题、年份、季集信息
- 📁 **多格式支持**: 支持电影和电视剧的标准化命名
- 🔄 **多种云盘**: 支持Alist、CD2等多种云盘挂载方式
- 📊 **嵌套识别**: 智能处理多季嵌套目录结构

#### 配置说明

1. **启用AI智能命名**: 开启后使用AI分析文件名
2. **DeepSeek API Key**: 在 https://platform.deepseek.com 申请API密钥
3. **监控目录配置**: 
   - 基础格式: `源目录#目标目录#媒体库路径`
   - CD2格式: `源目录#目标目录#cd2#挂载路径#服务地址`
   - Alist格式: `源目录#目标目录#alist#挂载路径#服务地址`

#### 使用方法

1. 在MoviePilot插件市场安装CloudStrmAI插件
2. 配置DeepSeek API Key和监控目录
3. 启用插件并设置定时任务
4. 插件将自动处理新增文件并生成Strm文件

## 安装方法

在MoviePilot的插件设置中，添加插件仓库地址：
```
https://github.com/dogzong/MoviePilot-Plugins
```

然后在插件市场中搜索并安装所需插件。

## 反馈与支持

如有问题或建议，请在GitHub Issues中反馈。

## 更新日志

### CloudStrmAI v1.0.1 (2024-10-03)
- 首次发布
- 支持AI智能命名功能
- 支持多种云盘挂载方式
- 支持电影和电视剧标准化处理
