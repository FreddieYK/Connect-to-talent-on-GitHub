# GitHub 项目分析工具 - Vercel 部署指南

## 🚀 部署架构

### 前端（Vercel）
- 静态网站托管
- 全球CDN加速
- 自动HTTPS

### 后端（推荐平台）
- **Railway**: 免费额度，支持Python，自动部署
- **Render**: 免费套餐，容器化部署  
- **Heroku**: 经典选择，但免费套餐已取消
- **PythonAnywhere**: 专为Python设计

## 📝 详细部署步骤

### 1. 准备代码仓库

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 推送到GitHub
git remote add origin https://github.com/yourusername/github-analysis-tool.git
git push -u origin main
```

### 2. 部署后端到Railway（推荐）

#### 2.1 创建Railway项目
1. 访问 [railway.app](https://railway.app)
2. 连接GitHub账户
3. 选择您的仓库
4. 选择部署分支

#### 2.2 配置环境变量
在Railway Dashboard中设置：
```
GITHUB_TOKEN=your_github_token_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PORT=8000
```

#### 2.3 创建Railway配置文件
Railway会自动检测Python项目，但您可以创建 `railway.toml`：

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 3. 部署前端到Vercel

#### 3.1 连接Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 连接GitHub账户
3. 导入您的项目仓库

#### 3.2 配置Vercel
- **Framework Preset**: Other
- **Root Directory**: ./（项目根目录）
- **Build Command**: `echo "Static site - no build needed"`
- **Output Directory**: ./（当前目录）

#### 3.3 设置环境变量
在Vercel Dashboard中添加：
```
BACKEND_URL=https://your-railway-app.railway.app
```

### 4. 更新API配置

部署后端成功后，更新前端配置：

1. 获取Railway提供的域名（例如：`https://your-app-production.up.railway.app`）
2. 在Vercel Dashboard中更新 `BACKEND_URL` 环境变量
3. 重新部署前端

### 5. 测试部署

访问您的Vercel域名，测试以下功能：
- ✅ 项目搜索建议
- ✅ 项目分析功能  
- ✅ 贡献者信息获取
- ✅ AI项目推荐

## 🔧 可选：Serverless函数部署

如果您想将后端也部署到Vercel，可以转换为Serverless函数：

### 创建API路由
在 `api/` 目录下创建Python函数：

```python
# api/suggestions.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

def handler(request):
    # 实现搜索建议逻辑
    pass
```

### 配置要求文件
```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
beautifulsoup4==4.12.2
pydantic==2.5.0
```

## 🚨 注意事项

1. **API密钥安全**: 绝不要在前端代码中硬编码API密钥
2. **CORS配置**: 确保后端正确配置CORS
3. **环境变量**: 使用平台的环境变量功能
4. **域名配置**: 部署后更新API_BASE_URL
5. **监控**: 设置错误监控和日志记录

## 📊 成本估算

- **Vercel**: 免费套餐足够使用
- **Railway**: 免费套餐 $5 credit/月
- **总成本**: 基本免费（小规模使用）

## 🆘 故障排除

### 常见问题
1. **CORS错误**: 检查后端CORS配置
2. **API连接失败**: 验证BACKEND_URL环境变量
3. **部署失败**: 检查requirements.txt和Python版本
4. **功能异常**: 查看浏览器控制台和服务器日志

### 调试技巧
```javascript
// 在浏览器控制台检查API配置
console.log('API Base URL:', API_BASE_URL);
```

## 🔄 持续部署

设置GitHub Actions自动部署：
- 推送到main分支自动部署
- PR预览环境
- 自动化测试

部署完成后，您将拥有一个完全可用的在线GitHub项目分析工具！🎉