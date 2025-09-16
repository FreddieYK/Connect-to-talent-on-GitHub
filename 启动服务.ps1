# GitHub爬虫工具启动脚本
# 作者: GitHub爬虫工具团队

Write-Host "🚀 GitHub爬虫工具启动中..." -ForegroundColor Green

# 设置工作目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = $ScriptDir
$StaticDir = Join-Path $ProjectDir "static"
$VenvPython = "D:\爬虫工具\.venv\Scripts\python.exe"

Write-Host "📁 项目目录: $ProjectDir" -ForegroundColor Cyan
Write-Host "📁 静态目录: $StaticDir" -ForegroundColor Cyan

# 检查必要文件
if (-not (Test-Path $StaticDir)) {
    Write-Host "❌ 静态目录不存在: $StaticDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $StaticDir "index.html"))) {
    Write-Host "❌ index.html文件不存在" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $StaticDir "script.js"))) {
    Write-Host "❌ script.js文件不存在" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 所有必要文件检查完成" -ForegroundColor Green

# 启动后端服务器
Write-Host "🔧 启动后端API服务器 (端口: 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectDir'; & '$VenvPython' main.py" -WindowStyle Normal

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务器
Write-Host "🌐 启动前端服务器 (端口: 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$StaticDir'; & '$VenvPython' -m http.server 3000" -WindowStyle Normal

# 等待前端启动
Start-Sleep -Seconds 3

Write-Host "🎉 服务启动完成！" -ForegroundColor Green
Write-Host "📱 前端地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 后端API: http://localhost:8000" -ForegroundColor Cyan

# 自动打开浏览器
Write-Host "🌍 正在打开浏览器..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host "✅ 启动完成！按任意键退出此窗口" -ForegroundColor Green
Read-Host