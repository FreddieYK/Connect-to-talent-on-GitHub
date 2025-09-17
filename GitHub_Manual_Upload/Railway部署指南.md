# Railway 后端 + Vercel 前端完整部署指南 🚀

## Railway界面变化说明 📋

**重要提醒：2024年Railway界面更新重点**
- Railway将环境变量配置从原来的"Settings" → "Environment"移动到了更明显的位置
- 新版本中**"Variables"**通常在项目顶部导航栏中直接可见
- 部分用户可能看到**"Environment Variables"**在左侧边栏
- 界面可能因账户类型或项目阶段而略有不同

**如果仍然找不到Variables选项，请尝试：**
1. 刷新页面或清除浏览器缓存
2. 查看项目是否已完全创建（有时需要等待几秒钟）
3. 在项目概览页面寻找任何配置相关的按钮
4. 直接联系Railway支持获取最新界面指导

## 完整部署架构

```
用户访问
    ↓
[Vercel 前端] (静态文件托管)
    ↓ API 调用
[Railway 后端] (FastAPI 服务)
    ↓ 数据获取
[GitHub API + DeepSeek AI]
```

**优势：**
- 前端：Vercel 全球 CDN 加速，免费静态托管
- 后端：Railway 稳定 API 服务，支持动态端口
- 成本：两个平台免费额度足够个人使用
- 维护：GitHub 推送自动触发部署更新

## 概述

将 FastAPI 后端部署到 Railway 平台可以完全解决当前 Vercel 静态部署遇到的 CORS 和 API 连接问题，实现真正的在线版本。

## 部署方案对比

### 当前状态（Vercel 静态部署）
- ❌ **问题**：无法连接后端 API，只能显示演示数据
- ❌ **限制**：CORS 错误，无法获取真实 GitHub 数据
- ✅ **优势**：部署简单，适合展示界面

### Railway + Vercel 完整方案
- ✅ **解决**：提供真实的 API 服务
- ✅ **功能**：完整的 GitHub 数据分析和 AI 推荐
- ✅ **用户体验**：真正的在线版本，无需本地部署
- ✅ **性能**：前端 CDN 加速 + 后端专业 API 服务
- ⚠️ **配置**：需要配置环境变量和 API 地址

## 部署步骤总览 📝

**完整部署流程分为两个阶段：**

### 阶段一：Railway 后端部署 (首先进行)
1. 准备部署文件
2. 创建Railway项目
3. 配置环境变量
4. 上传代码并部署
5. 获取API地址

### 阶段二：Vercel 前端配置 (后端部署成功后)
1. 更新前端 API 配置
2. 推送代码到 GitHub
3. Vercel 自动重新部署
4. 测试完整功能

**总耗时：15-30分钟**

---

# 阶段一：Railway 后端部署 🚀

## Railway 手动部署详细步骤

### 准备阶段：文件结构检查

确保项目包含以下必要文件：
```
fredd/
├── main.py              # FastAPI 主程序
├── models.py            # 数据模型定义
├── github_crawler.py    # GitHub 数据爬取
├── requirements.txt     # Python 依赖包
├── static/             # 前端静态文件
│   ├── index.html      # 主页面
│   ├── script.js       # 前端逻辑
│   └── styles.css      # 样式文件
└── .env.example        # 环境变量示例
```

### 第一步：创建 Railway 部署配置文件

在项目根目录创建以下配置文件：

#### 1. 创建 `railway.json`
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

#### 2. 创建 `Procfile`
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3. 创建/更新 `.gitignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
pip-log.txt
pip-delete-this-directory.txt
.DS_Store
Thumbs.db
*.log
```

### 第二步：Railway 平台操作

#### 1. 注册并登录 Railway
1. 访问 [Railway.app](https://railway.app/)
2. 点击 "Login" 使用 GitHub 账户登录
3. 完成账户验证和设置

#### 2. 创建新项目
1. 在 Railway 控制台点击 **"New Project"**
2. 选择 **"Empty Project"**
3. 为项目命名（如：`github-talent-analyzer`）
4. 点击 "Create Project"

#### 3. 配置项目设置
1. 进入项目详情页面
2. 点击 **"Settings"** 标签
3. 在 **"Environment"** 部分设置以下环境变量：

```
# 必需的环境变量
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PORT=8000
PYTHONPATH=/app

# 可选的环境变量
FASTAPI_ENV=production
CORS_ORIGINS=*
```

**重要**：DEEPSEEK_API_KEY 是必需的，用于 AI 推荐功能

#### 4. 上传项目文件

**方法一：GitHub 连接（推荐）**
1. 确保代码已推送到 GitHub 仓库
2. 在 Railway 项目中点击 **"Connect Repo"**
3. 选择 `FreddieYK/Connect-to-talent-on-GitHub` 仓库
4. 选择 `main` 分支
5. 点击 "Connect" 完成连接

**方法二：直接文件上传**
1. 在项目页面点击 **"Deploy"** 标签
2. 选择 **"Deploy from Local Directory"**
3. 将项目文件夹拖拽到上传区域
4. 等待文件上传完成

### 第三步：部署配置与验证

#### 1. 触发部署
1. 文件上传完成后，Railway 会自动检测到 Python 项目
2. 查看 **"Deployments"** 标签，确认构建开始
3. 监控构建日志，确保没有错误

#### 2. 检查部署状态
构建过程中会显示以下步骤：
```
✅ Installing dependencies from requirements.txt
✅ Setting up Python environment
✅ Starting uvicorn server
✅ Health check passed
✅ Deployment successful
```

#### 3. 获取部署 URL
1. 部署成功后，在项目概览页面找到生成的域名
2. 格式类似：`https://your-app-name.railway.app`
3. 记录此 URL，稍后配置前端时需要使用

#### 4. 验证 API 服务
访问以下端点验证部署：
- **健康检查**：`https://your-app.railway.app/api/health`
  - 预期响应：`{"status": "healthy", "version": "1.0.0"}`
- **API 文档**：`https://your-app.railway.app/docs`
  - 应显示完整的 FastAPI 文档界面

### 第四步：更新前端配置

#### 1. 修改 API 配置
更新 `static/script.js` 中的 API_BASE_URL：

```javascript
// API配置 - 支持多环境
const API_BASE_URL = (() => {
    // 生产环境：使用 Railway 部署的后端
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return 'https://your-app-name.railway.app'; // 替换为你的实际 Railway 域名
    }
    // 开发环境：本地后端
    return 'http://localhost:8000';
})();
```

#### 2. 重新部署前端
1. 提交前端配置更改：
```bash
git add static/script.js
git commit -m "feat: 配置Railway后端API地址"
git push origin main
```

2. Vercel 会自动重新部署前端

---

# 阶段二：Vercel 前端完整配置 🌐

## Vercel 部署概述

**前提条件：**
- Railway 后端已成功部署
- 已获取 Railway API 地址
- GitHub 仓库已更新最新代码

### 步骤 1：更新前端 API 配置

**重要：先更新前端配置，再进行 Vercel 部署**

#### 1.1 修改 script.js 中的 API 地址

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

#### 1.2 推送更改到 GitHub

```bash
cd 你的项目目录
git add static/script.js
git commit -m "feat: 连接Railway后端 API，启用完整功能"
git push origin main
```

### 步骤 2：Vercel 部署配置

#### 2.1 访问 Vercel 控制台

1. **登录 Vercel**
   - 访问 [vercel.com](https://vercel.com/)
   - 使用 GitHub 账户登录

2. **检查现有项目**
   - 在 Dashboard 中查找现有的项目
   - 如果已存在，点击进入项目设置

#### 2.2 创建或更新 Vercel 项目

**如果是新部署：**
1. 点击 **"New Project"**
2. 选择 **"Import Git Repository"**
3. 找到你的 GitHub 仓库 `Connect-to-talent-on-GitHub`
4. 点击 **"Import"**

**如果是更新现有项目：**
1. 进入项目详情页面
2. 点击 **"Deployments"** 标签
3. Vercel 会自动检测 GitHub 更新并触发部署

#### 2.3 配置部署设置

1. **Root Directory 设置**
   - 在项目设置中，确保 Root Directory 设置为 **"." (根目录)**
   - 或者留空（默认为根目录）

2. **Build 命令设置**
   - Build Command: **留空**（静态文件不需要构建）
   - Output Directory: **"static"**
   - Install Command: **留空**

3. **环境变量设置**
   - 在 **"Environment Variables"** 中可以添加（可选）：
   ```
   NODE_ENV=production
   ```

### 步骤 3：部署验证

#### 3.1 触发部署

1. **自动部署**
   - Vercel 检测到 GitHub 更新后会自动触发郤署
   - 在 **"Deployments"** 标签中查看部署进度

2. **手动触发**（如需）
   - 在项目设置中点击 **"Redeploy"**

#### 3.2 获取部署 URL

部署成功后，Vercel 会提供：
- **生产 URL**：`https://your-project-name.vercel.app`
- **预览 URL**：每次部署的独特 URL

### 步骤 4：完整功能测试

#### 4.1 基础功能检查

访问 Vercel 部署的 URL，逐一测试：

1. **页面加载**
   - ✅ 页面正常加载，无错误信息
   - ✅ 双标签页正常显示

2. **项目分析功能**
   - ✅ 输入GitHub项目名（如: `microsoft/vscode`）
   - ✅ 点击“开始分析”
   - ✅ 能获取真实的贡献者数据
   - ✅ 点击贡献者查看详细信息

3. **AI 智能推荐功能**
   - ✅ 在推荐标签页输入需求描述
   - ✅ 获取AI生成的项目推荐
   - ✅ 点击推荐项目可跳转到分析页面

4. **搜索建议功能**
   - ✅ 输入时显示项目建议
   - ✅ 点击建议可直接搜索

#### 4.2 性能和错误检查

1. **控制台检查**
   - 打开浏览器开发者工具 (F12)
   - 查看 Console 标签，确保无红色错误
   - 特别注意是否有 CORS 错误

2. **Network 标签检查**
   - 查看 API 请求是否成功
   - 确认 API 地址指向正确的 Railway 域名
   - 检查响应状态是否为 200

3. **错误排查**
   - 如果仍然显示演示数据，检查 API_BASE_URL 配置
   - 如果 API 调用失败，检查 Railway 后端是否正常运行

### 步骤 5：部署优化 (可选)

#### 5.1 自定义域名

1. 在 Vercel 项目设置中点击 **"Domains"**
2. 添加你的自定义域名
3. 配置 DNS 记录指向 Vercel

#### 5.2 性能监控

1. 在 Vercel Dashboard 查看项目的：
   - 访问量统计
   - 响应时间
   - 错误率

2. 在 Railway Dashboard 监控后端：
   - CPU 和内存使用量
   - API 请求量
   - 错误日志

---

# 部署成功验证清单 ✅

## 必须验证的功能

### 后端 API 验证
- ✅ 访问 Railway 健康检查：`https://your-app.railway.app/api/health`
- ✅ 返回 JSON: `{"status": "healthy", "version": "1.0.0"}`
- ✅ 访问 API 文档：`https://your-app.railway.app/docs`

### 前端功能验证
- ✅ 访问 Vercel 部署地址，页面正常加载
- ✅ 浏览器控制台无红色错误
- ✅ API 调用成功，不再显示演示数据

### 用户功能验证
- ✅ GitHub 项目分析正常工作
- ✅ AI 推荐功能正常工作
- ✅ 搜索建议正常显示
- ✅ 用户详情查看正常

## 成功标志

当以上所有项目都✅时，说明部署完全成功！

您现在拥有：
- 🌐 **全球可访问的在线版本**
- 🚀 **高性能的前后端分离架构**
- 🤖 **完整的 AI 智能推荐功能**
- 📊 **真实的 GitHub 数据分析**
- 💰 **零成本的云端部署**

### 第五步：测试完整功能

#### 1. 功能验证清单
- ✅ **项目分析**：输入 GitHub 项目名，获取贡献者数据
- ✅ **AI 推荐**：输入需求描述，获取项目推荐
- ✅ **搜索建议**：输入时显示项目建议
- ✅ **用户详情**：点击贡献者查看详细信息
- ✅ **无 CORS 错误**：浏览器控制台无跨域错误

#### 2. 性能监控
在 Railway 控制台监控：
- **CPU 使用率**
- **内存使用量**
- **请求响应时间**
- **错误日志**

## 完整架构方案

### 推荐架构：双平台部署
```
用户访问
    ↓
[Vercel 前端]
    ↓ API 调用
[Railway 后端]
    ↓ 数据获取
[GitHub API + DeepSeek AI]
```

**优势**：
- 前端：Vercel 的全球 CDN 加速
- 后端：Railway 的稳定 API 服务
- 成本：免费额度足够个人使用
- 维护：自动部署和更新

## 成本分析

### Railway 免费额度
- **每月** $5 免费额度
- **资源** 512MB 内存，0.5 vCPU
- **流量** 无限制
- **存储** 1GB

### 预期使用量
- **后端服务** 约 100-200MB 内存
- **API 调用** 轻量级，资源消耗低
- **数据存储** 主要是缓存，占用很少
- **结论** 免费额度完全够用

## 故障排除

### 常见部署问题

#### 1. 构建失败
**症状**：部署过程中出现错误
**解决方案**：
```bash
# 检查 requirements.txt 格式
cat requirements.txt

# 确保没有版本冲突
pip install -r requirements.txt

# 检查 Python 版本兼容性
python --version
```

#### 2. 服务启动失败
**症状**：健康检查失败，服务无法访问
**解决方案**：
1. 检查 Railway 日志：
   - 在项目页面点击 "Deployments"
   - 查看最新部署的日志输出
2. 验证环境变量配置
3. 确认端口配置正确（必须使用 $PORT）

#### 3. API 连接超时
**症状**：前端请求超时或失败
**解决方案**：
1. 检查 Railway 服务状态
2. 验证 CORS 配置
3. 确认前端 API_BASE_URL 正确

#### 4. DeepSeek API 错误
**症状**：AI 推荐功能无法使用
**解决方案**：
1. 验证 DEEPSEEK_API_KEY 环境变量
2. 检查 API 密钥有效性
3. 确认 API 调用配额

### 日志查看方法

1. **实时日志**：
   ```bash
   # 在 Railway 控制台
   项目 > Deployments > View Logs
   ```

2. **错误调试**：
   ```bash
   # 本地测试相同配置
   export DEEPSEEK_API_KEY="your_key"
   export PORT=8000
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 维护和更新

### 自动部署配置
如果使用 GitHub 连接，每次推送到 main 分支都会触发自动部署：

1. **代码更新流程**：
```bash
git add .
git commit -m "feat: 新功能或修复"
git push origin main
```

2. **监控部署状态**：
   - Railway 会发送邮件通知部署结果
   - 在控制台查看部署历史和状态

### 环境变量管理
1. 在 Railway 控制台更新环境变量
2. 重启服务使变量生效
3. 不要在代码中硬编码敏感信息

## 预期效果

部署 Railway 后端后，您的应用将实现：

1. ✅ **消除所有 CORS 错误**
2. ✅ **获取真实 GitHub 数据**
3. ✅ **支持完整 AI 智能推荐**
4. ✅ **提供专业级用户体验**
5. ✅ **无需用户本地部署**
6. ✅ **全球访问，稳定可靠**

## 技术支持

如果遇到问题，可以：
1. 查看 Railway 官方文档：https://docs.railway.app/
2. 检查项目的 GitHub Issues
3. 在 Railway 社区寻求帮助

---

**总结**：通过以上详细步骤，您可以将后端服务成功部署到 Railway，结合 Vercel 前端，实现完整的在线 GitHub 项目分析和 AI 推荐工具。整个过程大约需要 15-30 分钟，一次配置后即可享受自动化的部署和更新。