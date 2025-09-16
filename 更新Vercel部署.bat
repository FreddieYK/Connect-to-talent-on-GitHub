@echo off
chcp 65001 >nul
title Vercel部署更新工具

echo.
echo ==========================================
echo    Vercel 部署更新工具
echo    更新最新版本到生产环境
echo ==========================================
echo.

cd /d "%~dp0"

echo 📁 当前目录: %CD%
echo.

:: 检查Git状态
echo 🔍 检查Git状态...
git status

echo.
echo 📦 添加所有更改...
git add .

echo.
echo 💾 创建更新提交...
git commit -m "fix: 修复Vercel部署问题，更新到最新双功能版本

- 🔧 修复API配置问题
- 🎯 确保部署最新的双Tab界面
- 🌐 优化生产环境配置
- 📱 修复前端与后端连接"

echo.
echo 🚀 推送更新到GitHub...
git push origin main

if errorlevel 1 (
    echo ❌ 推送失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✅ 更新推送完成！
echo ==========================================
echo.
echo 📝 Vercel会自动检测到更改并重新部署
echo 🌐 请等待3-5分钟后访问你的Vercel URL
echo.
echo 💡 如果问题仍然存在，请检查：
echo    1. Vercel项目是否连接到正确的GitHub仓库
echo    2. 部署分支是否设置为main
echo    3. 环境变量是否正确配置
echo.

echo 🌍 正在打开Vercel控制台...
start https://vercel.com/dashboard

echo.
echo 按任意键关闭窗口...
pause >nul