# GitHub 项目分析工具 - Railway + Vercel 完整部署指南 🚀

本指南提供从零开始的完整部署流程，实现真正的在线版本。

## 🏗️ 部署架构

```
用户访问 → [Vercel 前端] → [Railway 后端] → [GitHub API + DeepSeek AI]
```

**优势：**
- 🌐 **前端**：Vercel 全球 CDN 加速，免费静态托管
- ⚡ **后端**：Railway 专业 API 服务，支持动态扩展
- 💰 **成本**：两平台免费额度足够个人使用
- 🔄 **维护**：GitHub 推送自动触发双平台更新

## 📋 部署前准备

### 必需的账户和资源
1. **GitHub 账户** - 代码托管 ([github.com](https://github.com/))
2. **Railway 账户** - 后端部署 ([railway.app](https://railway.app/))
3. **Vercel 账户** - 前端部署 ([vercel.com](https://vercel.com/))
4. **DeepSeek API 密钥** - AI 推荐功能 ([platform.deepseek.com](https://platform.deepseek.com/))

### 环境要求
- Git 已安装并配置
- 有效的网络连接
- 现代浏览器（用于测试）

### 部署时间估算
- **Railway 后端部署**: 10-15 分钟
- **Vercel 前端配置**: 5-10 分钟
- **总计**: 20-30 分钟

---

# 第一阶段：Railway 后端部署 🚂

> **重要：必须先完成后端部署，获取 API 地址后再配置前端**

## 步骤 1：准备部署配置文件

在开始 Railway 部署之前，确保项目已包含正确的配置文件：

### 1.1 检查 railway.json
确保项目根目录有 `railway.json` 文件：
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "always"
  }
}
```

### 1.2 检查 Procfile
确保项目根目录有 `Procfile` 文件：
```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**关键修复**：使用 `${PORT:-8000}` 语法替代 `$PORT`，解决端口配置错误。

## 步骤 2：创建 Railway 项目

### 2.1 注册并登录 Railway
1. 访问 [railway.app](https://railway.app/)
2. 点击 "Login" 使用 GitHub 账户登录
3. 完成账户验证

### 2.2 创建新项目
1. 在控制台点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 授权 Railway 访问你的 GitHub 仓库
4. 选择你的项目仓库
5. 选择 `main` 分支
6. 点击 "Deploy"

## 步骤 3：配置环境变量

### 3.1 找到环境变量设置
Railway 新界面中环境变量位置：
- 在项目页面点击 **"Variables"** 标签（通常在顶部导航栏）
- 或在左侧菜单中找到 **"Environment Variables"**

### 3.2 添加必需的环境变量
点击 "New Variable" 添加以下变量：

```bash
# 必需配置
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
PORT=8000

# 可选配置
PYTHONPATH=/app
FASTAPI_ENV=production
CORS_ORIGINS=*
```

**重要**：
- `DEEPSEEK_API_KEY` 是必需的，从 [platform.deepseek.com](https://platform.deepseek.com/) 获取
- `PORT=8000` 确保端口配置正确

## 步骤 4：监控部署过程

### 4.1 查看构建日志
1. 点击 **"Deployments"** 标签
2. 查看最新部署的状态
3. 点击部署项查看详细日志

### 4.2 验证构建成功
正常的构建日志应显示：
```
✅ Installing dependencies from requirements.txt
✅ Setting up Python environment
✅ Starting uvicorn server
✅ Health check passed
✅ Deployment successful
```

## 步骤 5：获取 API 地址

### 5.1 获取域名
部署成功后：
1. 在项目概览页面找到生成的域名
2. 格式类似：`https://your-app-name.railway.app`
3. **重要**：记录此 URL，配置前端时需要使用

### 5.2 验证后端服务
访问以下端点验证部署：
- **健康检查**：`https://your-app.railway.app/api/health`
  - 应返回：`{"status": "healthy", "version": "1.0.0"}`
- **API 文档**：`https://your-app.railway.app/docs`
  - 应显示完整的 FastAPI 文档界面

---

# 第二阶段：Vercel 前端配置 🌐


## 步骤 1：更新前端 API 配置

### 1.1 修改 script.js 中的 API 地址
找到 `static/script.js` 文件中的 `API_BASE_URL` 配置：

```javascript
// 修改前（静态演示模式）
const API_BASE_URL = (() => {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return null; // 静态部署环境，API不可用
    }
    return 'http://localhost:8000';
})();

// 修改后（连接 Railway 后端）
const API_BASE_URL = (() => {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return 'https://your-railway-domain.railway.app'; // 替换为实际的 Railway 域名
    }
    return 'http://localhost:8000';
})();
```

**关键点：**
- 将 `return null;` 改为 `return 'https://your-railway-domain.railway.app';`
- 确保 Railway 域名正确（从 Railway 控制台获取）
- 保留 `https://` 前缀

### 1.2 推送更改到 GitHub
```bash
cd 你的项目目录
git add static/script.js
git commit -m "feat: 连接Railway后端 API，启用完整功能"
git push origin main
```

## 步骤 2：Vercel 部署配置

### 2.1 访问 Vercel 控制台
1. 登录 [vercel.com](https://vercel.com/) 使用 GitHub 账户
2. 在 Dashboard 中查找现有项目

### 2.2 创建或更新项目
**新部署：**点击 "New Project" > "Import Git Repository" > 选择仓库
**更新：**进入项目 > "Deployments" > 自动检测更新

### 2.3 配置设置
- Root Directory: "." （根目录）
- Build Command: 留空
- Output Directory: "static"

## 步骤 3：功能测试与验证

### 必须验证的功能
**后端 API 验证**
- ✅ 访问：`https://your-app.railway.app/api/health`
- ✅ 返回：`{"status": "healthy", "version": "1.0.0"}`
- ✅ API 文档：`https://your-app.railway.app/docs`

**前端功能验证**
- ✅ 页面正常加载，无控制台错误
- ✅ GitHub 项目分析正常工作
- ✅ AI 推荐功能正常工作
- ✅ 搜索建议正常显示

### 故障排除
**仍显示演示数据：**
1. 检查 `API_BASE_URL` 配置
2. 确认 Railway 域名正确
3. 验证代码已推送并触发 Vercel 重新部署

**API 调用失败：**
1. 检查 Railway 后端状态
2. 验证健康检查端点
3. 查看 Railway 部署日志

---

# 部署成功标志 🎉

当所有功能都 ✅ 时，您就拥有了：
- 🌐 全球可访问的在线版本
- 🚀 高性能前后端分离架构
- 🤖 完整的 AI 智能推荐功能
- 📊 真实的 GitHub 数据分析
- 💰 零成本的云端部署

**部署时间：**20-30分钟，一次配置后享受自动化部署和更新。

**技术支持：**
- Railway: [docs.railway.app](https://docs.railway.app/)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- 项目 Issues 反馈