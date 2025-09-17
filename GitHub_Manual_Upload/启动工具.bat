@echo off
chcp 65001 >nul
title GitHub爬虫工具 - 一键启动

echo.
echo ==========================================
echo    GitHub 爬虫工具 - 本地开发环境启动
echo ==========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 进入项目目录
cd /d "%~dp0"

echo 📁 当前目录: %CD%
echo.

:: 检查虚拟环境
if not exist ".venv" (
    echo 🔧 创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 安装/更新依赖
echo 📦 检查并安装依赖...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install fastapi uvicorn requests beautifulsoup4 python-multipart python-dotenv pydantic

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成
echo.

:: 启动后端服务器（8000端口）
echo 🚀 启动后端API服务器 (端口: 8000)...
start "GitHub爬虫工具-后端API" cmd /k "cd /d \"%CD%\" && .venv\Scripts\python.exe main.py"

:: 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 3 /nobreak >nul

:: 启动前端开发服务器（3000端口）
echo 🌐 启动前端开发服务器 (端口: 3000)...
start "GitHub爬虫工具-前端界面" cmd /k "cd /d \"%CD%\" && .venv\Scripts\python.exe frontend_server.py"

:: 等待前端启动
echo ⏳ 等待前端服务启动...
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo 🎉 启动完成！
echo ==========================================
echo.
echo 📱 前端地址: http://localhost:3000
echo 🔧 后端API: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo.
echo 💡 提示:
echo    - 前端运行在3000端口，提供用户界面
echo    - 后端运行在8000端口，提供API服务
echo    - 浏览器会自动打开前端页面
echo    - 按 Ctrl+C 停止相应的服务器
echo.
echo ==========================================

:: 自动打开浏览器
echo 🌍 正在打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ✅ 所有服务已启动，按任意键关闭此窗口
pause >nul