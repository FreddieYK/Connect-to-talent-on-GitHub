@echo off
chcp 65001 >nul
title Railway后端部署工具

echo.
echo ==========================================
echo         Railway 后端部署工具
echo    解决Vercel静态部署的API连接问题
echo ==========================================
echo.

cd /d "%~dp0"

echo 📁 当前目录: %CD%
echo.

:: 检查必要文件
echo [1/6] 🔍 检查项目文件...
if not exist "main.py" (
    echo ❌ 未找到 main.py 文件，这不是一个有效的FastAPI项目
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ 未找到 requirements.txt 文件
    pause
    exit /b 1
)

echo ✅ 项目文件检查完成

:: 安装Railway CLI
echo.
echo [2/6] 🚂 检查Railway CLI...
railway version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Railway CLI 未安装，正在安装...
    
    :: 检查是否有npm
    npm --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 需要安装 Node.js 和 npm
        echo 请先安装 Node.js: https://nodejs.org/
        pause
        exit /b 1
    )
    
    echo 正在安装 Railway CLI...
    npm install -g @railway/cli
    
    if errorlevel 1 (
        echo ❌ Railway CLI 安装失败
        echo 请手动安装: npm install -g @railway/cli
        pause
        exit /b 1
    )
    
    echo ✅ Railway CLI 安装成功
) else (
    echo ✅ Railway CLI 已安装
)

:: 创建Railway配置文件
echo.
echo [3/6] ⚙️  创建Railway配置...

:: 创建 railway.json
if not exist "railway.json" (
    echo 创建 railway.json...
    (
    echo {
    echo   "$schema": "https://railway.app/railway.schema.json",
    echo   "build": {
    echo     "builder": "nixpacks"
    echo   },
    echo   "deploy": {
    echo     "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    echo     "healthcheckPath": "/api/health",
    echo     "healthcheckTimeout": 300,
    echo     "restartPolicyType": "always"
    echo   }
    echo }
    ) > railway.json
    echo ✅ railway.json 创建完成
) else (
    echo ✅ railway.json 已存在
)

:: 创建 Procfile
if not exist "Procfile" (
    echo 创建 Procfile...
    echo web: uvicorn main:app --host 0.0.0.0 --port $PORT > Procfile
    echo ✅ Procfile 创建完成
) else (
    echo ✅ Procfile 已存在
)

:: 推送代码更改
echo.
echo [4/6] 📦 推送配置到GitHub...
git add railway.json Procfile
git commit -m "feat: 添加Railway部署配置

- ➕ 新增railway.json部署配置
- ➕ 新增Procfile进程定义
- 🚀 准备Railway后端部署以解决API连接问题"

git push origin main
if errorlevel 1 (
    echo ⚠️  推送失败，但继续部署流程...
)

:: Railway登录和部署
echo.
echo [5/6] 🔐 Railway登录...
echo.
echo 即将打开浏览器进行Railway登录认证...
echo 请在浏览器中完成登录后，回到此窗口继续...
echo.
pause

railway login

if errorlevel 1 (
    echo ❌ Railway登录失败
    pause
    exit /b 1
)

echo ✅ Railway登录成功

:: 初始化项目
echo.
echo [6/6] 🚀 初始化并部署项目...
echo.
echo 正在创建Railway项目...
railway init

if errorlevel 1 (
    echo ❌ 项目初始化失败
    pause
    exit /b 1
)

echo.
echo 🔧 配置环境变量...
echo.
echo 重要：需要配置DeepSeek API密钥才能使用AI推荐功能
echo.
set /p "api_key=请输入您的DeepSeek API密钥（可以稍后在Railway控制台配置）: "

if not "%api_key%"=="" (
    railway variables set DEEPSEEK_API_KEY="%api_key%"
    echo ✅ API密钥配置完成
) else (
    echo ⚠️  API密钥跳过，请稍后在Railway控制台手动配置
)

:: 设置其他环境变量
railway variables set PORT=8000
railway variables set PYTHONPATH=/app

echo.
echo 🚀 开始部署...
railway deploy

if errorlevel 1 (
    echo ❌ 部署失败
    echo.
    echo 可能的解决方案：
    echo 1. 检查网络连接
    echo 2. 确保Railway账户有足够配额
    echo 3. 检查代码是否有语法错误
    echo 4. 查看Railway控制台日志
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✅ Railway后端部署完成！
echo ==========================================
echo.
echo 📋 部署信息：
railway status
echo.

:: 获取部署URL
echo 🌐 获取部署URL...
railway domain
echo.

echo 📝 下一步操作：
echo.
echo 1. 📋 记下上面显示的Railway域名（类似：https://your-app.railway.app）
echo 2. 📝 更新前端代码中的API_BASE_URL配置
echo 3. 🔄 重新部署Vercel前端
echo 4. 🎉 享受完整的在线功能！
echo.
echo 💡 提示：
echo   • Railway会自动从GitHub拉取代码
echo   • 每次推送main分支都会触发自动部署
echo   • 可以在Railway控制台查看日志和监控
echo.

echo 🌍 正在打开Railway控制台...
start https://railway.app/dashboard

echo.
echo ==========================================
echo              部署完成
echo ==========================================
echo.
echo 现在您可以：
echo 1. 在Railway控制台查看后端服务状态
echo 2. 测试API接口：https://your-domain.railway.app/api/health
echo 3. 更新前端配置以连接新的后端
echo 4. 享受无CORS限制的完整功能
echo.
echo 按任意键关闭窗口...
pause >nul