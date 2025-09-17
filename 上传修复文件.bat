@echo off
chcp 65001 >nul
echo.
echo ====================================
echo    🔧 修复Railway后端HTML显示问题
echo ====================================
echo.
echo 📋 问题诊断：
echo    Railway后端不应该显示HTML页面
echo    后端应该只提供JSON API响应
echo    当前后端错误地服务了静态文件
echo.

echo 📂 检查项目状态...
if not exist "main.py" (
    echo ❌ 错误：找不到 main.py 文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

echo ✅ 项目文件检查完成
echo.

echo 📝 准备上传修复后的后端代码：
echo    - main.py (纯API后端，无静态文件服务)
echo    - railway.toml (Railway配置)
echo    - requirements.txt (依赖)
echo    - 其他必要的Python文件
echo.

echo 🚀 开始Git操作...

echo 添加所有修改的文件...
git add .

echo 提交修改...
git commit -m "🔧 紧急修复：Railway后端不应返回HTML页面

问题：
- Railway后端错误地显示HTML页面而不是JSON API
- 后端应该只提供API服务，不应服务静态文件

修复：
- 确保main.py只包含API端点
- 移除所有静态文件服务代码
- Railway只提供后端API服务
- 前端由Vercel单独部署"

echo 推送到GitHub...
git push origin main

echo.
echo ✅ 修复上传完成！
echo.
echo 📋 接下来Railway会自动重新部署：
echo    1. Railway检测到代码更新 (约30秒)
echo    2. 重新构建后端服务 (约2-3分钟)
echo    3. 部署纯API后端 (约1分钟)
echo.
echo 🔍 验证修复结果：
echo    后端API测试：
echo    https://connect-to-talent-on-github-production.up.railway.app/api/health
echo    
echo    应该返回JSON：{"status":"healthy","message":"API服务正常运行"}
echo    而不是HTML页面
echo.
echo 🌐 完整架构：
echo    前端(Vercel): 用户界面
echo    后端(Railway): 纯API服务
echo.
echo ⏱️  等待约5分钟后测试API端点
echo.
pause