@echo off
chcp 65001 >nul
echo.
echo ====================================
echo    🚀 修复Vercel部署静态资源问题
echo ====================================
echo.
echo 📋 问题诊断：
echo    1. JavaScript语法错误: Unexpected token '<'
echo    2. CSS样式缺失，页面显示简单HTML
echo    3. Vercel配置不正确，静态资源路径错误
echo.

echo 📂 检查项目状态...
if not exist "static\index.html" (
    echo ❌ 错误：找不到 static\index.html 文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

echo ✅ 项目文件检查完成
echo.

echo 📝 修复内容：
echo    - 修夏vercel.json配置（简化为最基本配置）
echo    - 修夏HTML中的CSS/JS路径引用
echo    - 更新后端CORS配置支持Vercel域名
echo    - 确保前端API正确连接Railway后端
echo.

echo 🚀 开始Git操作...

echo 添加所有修改的文件...
git add .

echo 提交修改...
git commit -m "🔧 紧急修复：Vercel部署静态资源加载问题

问题：
- JavaScript语法错误: Unexpected token '<'
- CSS样式缺失，页面显示简单HTML
- Vercel配置不正确导致资源路径错误

修复：
- 简化vercel.json为最基本配置
- 修夏HTML中的资源路径引用
- 更新后端CORS支持Vercel域名
- 确保前后端正确连接"

echo 推送到GitHub...
git push origin main

echo.
echo ✅ 修复上传完成！
echo.
echo 📋 接下来的步骤：
echo    1. Railway会自动重新部署后端 (约2-3分钟)
echo    2. Vercel会自动重新部署前端 (约1-2分钟)  
echo    3. 等待部署完成后测试功能
echo.
echo 🌐 部署后验证：
echo    ✓ 前端页面能正常加载（有CSS样式）
echo    ✓ JavaScript功能正常无语法错误
echo    ✓ 搜索和AI推荐功能能连接后端
echo    ✓ 浏览器控制台无错误信息
echo.
echo 🔍 如果仍有问题：
echo    - 检查Vercel部署日志
echo    - 确认Root Directory设置为项目根目录
echo    - 检查浏览器开发者工具网络面板
echo.
pause