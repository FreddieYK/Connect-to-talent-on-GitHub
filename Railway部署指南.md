# Railway 后端部署指南 🚀

## 概述

将 FastAPI 后端部署到 Railway 平台可以完全解决当前 Vercel 静态部署遇到的 CORS 和 API 连接问题，实现真正的在线版本。

## 部署方案对比

### 当前状态（Vercel 静态部署）
- ❌ **问题**：无法连接后端 API，只能显示演示数据
- ❌ **限制**：CORS 错误，无法获取真实 GitHub 数据
- ✅ **优势**：部署简单，适合展示界面

### Railway 后端部署方案
- ✅ **解决**：提供真实的 API 服务
- ✅ **功能**：完整的 GitHub 数据分析和 AI 推荐
- ✅ **用户体验**：真正的在线版本，无需本地部署
- ⚠️ **注意**：需要配置环境变量（DeepSeek API 密钥）

## 部署步骤详解

### 步骤 1: 准备工作

1. **确保代码最新**
   ```bash
   git add .
   git commit -m "prepare for railway deployment"
   git push origin main
   ```

2. **检查项目结构**
   ```
   fredd/
   ├── main.py              # FastAPI 主程序
   ├── requirements.txt     # Python 依赖
   ├── Procfile            # 可选：进程定义
   ├── railway.json        # 可选：Railway 配置
   └── static/             # 前端文件
   ```

### 步骤 2: 创建 Railway 部署配置

创建 `railway.json` 文件：
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "always"
  }
}
```

创建 `Procfile` 文件：
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 步骤 3: Railway 平台部署

1. **注册 Railway 账户**
   - 访问 [Railway.app](https://railway.app/)
   - 使用 GitHub 账户登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `FreddieYK/Connect-to-talent-on-GitHub` 仓库

3. **配置环境变量**
   ```bash
   # 在 Railway 项目设置中添加：
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   PORT=8000
   PYTHONPATH=/app
   ```

4. **配置自定义域名（可选）**
   - Railway 会自动生成域名：`https://your-app-name.railway.app`
   - 可以配置自定义域名

### 步骤 4: 更新前端配置

修改 `static/script.js` 中的 API 配置：
```javascript
const API_BASE_URL = (() => {
    // 生产环境：使用 Railway 部署的后端
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return 'https://your-app-name.railway.app'; // 替换为你的 Railway 域名
    }
    // 开发环境：本地后端
    return 'http://localhost:8000';
})();
```

### 步骤 5: 重新部署前端

更新前端配置后，重新部署到 Vercel：
```bash
git add .
git commit -m "update: 配置 Railway 后端 API 地址"
git push origin main
```

## 完整架构方案

### 方案 A: 双平台部署（推荐）
- **前端**：继续使用 Vercel 部署静态文件
- **后端**：使用 Railway 部署 FastAPI 服务
- **优势**：各司其职，性能最佳，成本较低

### 方案 B: Railway 全栈部署
- **全栈**：在 Railway 上同时部署前端和后端
- **优势**：统一管理，无跨域问题
- **劣势**：成本稍高，配置稍复杂

## 成本分析

### Railway 免费额度
- **每月** $5 免费额度
- **资源** 512MB 内存，0.5 vCPU
- **流量** 无限制
- **适用性** 足够支撑个人项目和演示

### 预期使用量
- **后端服务** 约 100-200MB 内存
- **API 调用** 轻量级，资源消耗低
- **结论** 免费额度完全够用

## 预期效果

部署 Railway 后端后，您的 Vercel 前端将：

1. ✅ **消除 CORS 错误**
2. ✅ **获取真实 GitHub 数据**
3. ✅ **支持 AI 智能推荐**
4. ✅ **提供完整用户体验**
5. ✅ **无需本地部署**

## 故障排除

### 常见问题

1. **部署失败**
   ```bash
   # 检查日志
   railway logs
   # 检查构建状态
   railway status
   ```

2. **API 连接超时**
   - 检查 Railway 服务状态
   - 验证环境变量配置
   - 确认健康检查端点

3. **CORS 问题**
   - 确保后端正确配置 CORS 中间件
   - 检查前端 API 地址配置

## 下一步

1. **立即体验**：运行 `Railway部署.bat` 自动化脚本
2. **手动部署**：按照上述步骤逐步配置
3. **监控运行**：使用 Railway 控制台监控服务状态

部署完成后，您将拥有一个真正的在线 GitHub 项目分析和 AI 推荐工具！ 🎉