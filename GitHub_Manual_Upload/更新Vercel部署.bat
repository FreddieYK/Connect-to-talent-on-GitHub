@echo off
chcp 65001 >nul
title Vercel部署更新工具

echo.
echo ==========================================
echo           更新 Vercel 部署
echo          （修复版本 v2.1）
echo ==========================================
echo.

cd /d "%~dp0"

echo 📁 当前目录: %CD%
echo.

:: 检查必要文件
echo [1/4] 🔍 检查必要文件...
if not exist "static\script.js" (
    echo ❌ 未找到 static/script.js 文件
    pause
    exit /b 1
)

:: 检查是否包含最新修复
echo [2/4] 🔧 验证修复内容...
findstr /C:"isStaticDemo" static\script.js >nul
if errorlevel 1 (
    echo ❌ 警告：script.js 可能不包含最新的修复代码
    echo    请确保已应用最新的错误修复补丁
    pause
) else (
    echo ✅ 检测到最新的静态演示功能代码
)

findstr /C:"showDemoWelcome" static\script.js >nul
if errorlevel 1 (
    echo ❌ 警告：缺少演示欢迎功能
    echo    部署后可能无法正确显示静态演示
    pause
) else (
    echo ✅ 演示功能代码完整
)

echo.
echo [3/4] 📦 推送最新更改到GitHub...
git status

echo.
echo 📦 添加所有更改...
git add .

echo.
echo 💾 创建更新提交...
git commit -m "fix: 修复Vercel部署的CORS和API连接错误

- ✨ 新增静态演示模式，解决API连接失败问题
- 🌐 优化生产环境错误处理和用户提示
- 🚀 添加演示数据和交互功能，提升用户体验
- 📚 提供完整的本地部署指导和说明文档
- 🔧 修复多标签页状态管理和请求取消问题"

echo.
echo 🚀 推送更新到GitHub...
git push origin main

if errorlevel 1 (
    echo ❌ 推送失败，尝试重新推送...
    git push origin main --force-with-lease
    if errorlevel 1 (
        echo ❌ 推送仍然失败
        echo.
        echo 可能的解决方案：
        echo 1. 检查网络连接
        echo 2. 检查Git凭据：git config --list
        echo 3. 手动推送：git push origin main
        pause
        exit /b 1
    )
)

echo.
echo [4/4] ✅ 部署更新完成！
echo.
echo ==========================================
echo ✨ 更新内容摘要
echo ==========================================
echo 🔧 修复CORS和API连接错误
echo 🌐 新增静态演示模式
echo 🚀 优化用户体验和错误提示
echo 📚 添加完整部署指导
echo 📱 修复多标签页状态管理
echo ==========================================
echo.
echo 📝 Vercel会自动检测到更改并重新部署
echo 🌐 请等待3-5分钟后访问你的Vercel URL
echo.
echo 💡 现在的部署版本将：
echo    • 在静态环境下显示演示数据
echo    • 提供清晰的错误提示和解决方案
echo    • 引导用户进行本地部署以获得完整功能
echo.
echo 🌍 正在打开Vercel控制台...
start https://vercel.com/dashboard

echo.
echo 按任意键关闭窗口...
pause >nul