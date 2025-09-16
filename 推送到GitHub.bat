@echo off
chcp 65001 >nul
title GitHub项目推送工具 - FreddieYK/Connect-to-talent-on-GitHub

echo.
echo ==========================================
echo    GitHub 项目推送工具
echo    目标仓库: FreddieYK/Connect-to-talent-on-GitHub
echo ==========================================
echo.

:: 进入项目目录
cd /d "%~dp0"

:: 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Git，请先安装Git
    echo 📥 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo 📁 当前目录: %CD%
echo.

:: 检查是否已经是Git仓库
if not exist ".git" (
    echo 🔧 初始化Git仓库...
    git init
    echo ✅ Git仓库初始化完成
) else (
    echo ✅ 检测到现有Git仓库
)

:: 添加远程仓库（如果不存在）
echo 🔗 配置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/FreddieYK/Connect-to-talent-on-GitHub.git

if errorlevel 1 (
    echo ❌ 添加远程仓库失败
    pause
    exit /b 1
)

echo ✅ 远程仓库配置完成

:: 检查用户配置
echo 👤 检查Git用户配置...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo 设置Git用户名...
    git config user.name "FreddieYK"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    echo 设置Git邮箱...
    set /p email="请输入你的GitHub邮箱: "
    git config user.email "%email%"
)

echo ✅ 用户配置完成

:: 添加所有文件
echo 📦 添加项目文件...
git add .

if errorlevel 1 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)

echo ✅ 文件添加完成

:: 创建提交
echo 💾 创建提交...
git commit -m "feat: 完整的GitHub项目分析和智能推荐工具

- ✨ 双功能设计：项目分析 + 智能推荐
- 🎨 现代化UI界面，玻璃质感设计
- 🔍 GitHub项目贡献者深度分析
- 🤖 基于自然语言的项目推荐
- 📱 响应式设计，支持移动端
- 🚀 一键启动脚本，便捷开发体验
- 🔧 FastAPI后端 + 纯前端架构
- 📊 实时数据获取和可视化展示"

if errorlevel 1 (
    echo ⚠️ 提交创建失败（可能没有更改）
)

echo ✅ 提交创建完成

:: 推送到GitHub
echo 🚀 推送到GitHub...
echo.
echo 📌 注意：如果这是第一次推送，GitHub会要求你登录
echo    1. 浏览器会自动打开GitHub登录页面
echo    2. 使用Google账号登录GitHub
echo    3. 完成验证后推送会自动继续
echo.
echo 正在推送到 main 分支...

git push -u origin main

if errorlevel 1 (
    echo.
    echo ⚠️ 推送失败，尝试强制推送...
    echo 注意：这会覆盖远程仓库的内容
    set /p confirm="确认强制推送？(y/N): "
    if /i "%confirm%"=="y" (
        git push -u origin main --force
    ) else (
        echo 取消推送操作
        pause
        exit /b 1
    )
)

echo.
echo ==========================================
echo 🎉 推送完成！
echo ==========================================
echo.
echo 📱 仓库地址: https://github.com/FreddieYK/Connect-to-talent-on-GitHub
echo 🌐 在线预览: https://freddieyk.github.io/Connect-to-talent-on-GitHub
echo.
echo 💡 接下来可以：
echo    1. 在GitHub仓库设置中启用GitHub Pages
echo    2. 配置域名和SSL证书
echo    3. 设置自动部署workflow
echo.
echo ==========================================

:: 自动打开GitHub仓库页面
echo 🌍 正在打开GitHub仓库...
start https://github.com/FreddieYK/Connect-to-talent-on-GitHub

echo.
echo ✅ 推送完成，按任意键关闭窗口
pause >nul