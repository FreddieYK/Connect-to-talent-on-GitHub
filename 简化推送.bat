@echo off
chcp 65001 >nul
title 推送到GitHub - 简化版

echo.
echo ==========================================
echo    推送项目到GitHub仓库
echo    FreddieYK/Connect-to-talent-on-GitHub
echo ==========================================
echo.

cd /d "%~dp0"

echo 当前目录: %CD%
echo.

echo 检查Git状态...
git status

echo.
echo 添加所有更改...
git add .

echo.
echo 检查是否有新的更改...
git status

echo.
echo 创建提交（如果有更改）...
git commit -m "feat: 更新项目文件，新增GitHub推送功能和完整的README文档"

echo.
echo ==========================================
echo 开始推送到GitHub...
echo ==========================================
echo.

echo 推送方式1: 使用GitHub认证
git push origin main

if errorlevel 1 (
    echo.
    echo 推送失败，请检查：
    echo 1. 网络连接是否正常
    echo 2. GitHub仓库是否存在
    echo 3. 是否需要身份验证
    echo.
    echo 请手动执行: git push origin main
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 推送成功！
echo ==========================================
echo.
echo GitHub仓库: https://github.com/FreddieYK/Connect-to-talent-on-GitHub
echo.

start https://github.com/FreddieYK/Connect-to-talent-on-GitHub

echo 按任意键关闭窗口...
pause >nul