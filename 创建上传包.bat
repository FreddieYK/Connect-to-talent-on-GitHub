@echo off
chcp 65001 >nul
title 创建GitHub手动上传包

echo.
echo ==========================================
echo    创建GitHub手动上传包
echo    准备手动上传到GitHub的文件
echo ==========================================
echo.

cd /d "%~dp0"

:: 创建上传包目录
set UPLOAD_DIR=GitHub_Upload_Package
if exist "%UPLOAD_DIR%" rmdir /s /q "%UPLOAD_DIR%"
mkdir "%UPLOAD_DIR%"

echo 📁 创建上传包目录: %UPLOAD_DIR%
echo.

:: 复制核心文件
echo 📦 复制项目文件...

:: 静态文件（前端）
echo - 复制前端文件...
xcopy "static" "%UPLOAD_DIR%\static" /E /I /Q
if errorlevel 1 echo ❌ 复制static失败

:: 后端文件
echo - 复制后端文件...
copy "main.py" "%UPLOAD_DIR%\" >nul
copy "frontend_server.py" "%UPLOAD_DIR%\" >nul
copy "github_crawler.py" "%UPLOAD_DIR%\" >nul
copy "models.py" "%UPLOAD_DIR%\" >nul

:: 配置文件
echo - 复制配置文件...
copy "requirements.txt" "%UPLOAD_DIR%\" >nul
copy "vercel.json" "%UPLOAD_DIR%\" >nul
copy ".env.example" "%UPLOAD_DIR%\" >nul
copy ".gitignore" "%UPLOAD_DIR%\" >nul

:: 文档文件
echo - 复制文档文件...
copy "README.md" "%UPLOAD_DIR%\" >nul
copy "LICENSE" "%UPLOAD_DIR%\" >nul

:: 脚本文件
echo - 复制脚本文件...
copy "启动工具.bat" "%UPLOAD_DIR%\" >nul
copy "推送到GitHub.bat" "%UPLOAD_DIR%\" >nul

:: GitHub Actions
echo - 复制GitHub Actions...
xcopy ".github" "%UPLOAD_DIR%\.github" /E /I /Q

:: API目录
echo - 复制API文件...
xcopy "api" "%UPLOAD_DIR%\api" /E /I /Q

echo.
echo ==========================================
echo ✅ 上传包创建完成！
echo ==========================================
echo.
echo 📁 上传包位置: %CD%\%UPLOAD_DIR%
echo.
echo 📋 包含的文件：
echo    ├── static/           (前端文件)
echo    ├── .github/          (GitHub Actions)
echo    ├── api/              (API文件)
echo    ├── main.py           (后端主程序)
echo    ├── frontend_server.py (前端服务器)
echo    ├── github_crawler.py  (爬虫模块)
echo    ├── models.py          (数据模型)
echo    ├── requirements.txt   (Python依赖)
echo    ├── vercel.json        (部署配置)
echo    ├── .env.example       (环境变量示例)
echo    ├── .gitignore         (Git忽略文件)
echo    ├── README.md          (项目说明)
echo    ├── LICENSE            (开源协议)
echo    ├── 启动工具.bat        (启动脚本)
echo    └── 推送到GitHub.bat    (推送脚本)
echo.
echo 🌍 正在打开上传包目录...
start "" "%CD%\%UPLOAD_DIR%"

echo.
echo 💡 接下来请按照以下步骤手动上传：
echo    1. 访问 https://github.com/FreddieYK/Connect-to-talent-on-GitHub
echo    2. 点击 "Add file" → "Upload files"
echo    3. 将上传包中的所有文件拖拽到GitHub
echo    4. 填写提交信息后点击 "Commit changes"
echo.

echo 按任意键关闭窗口...
pause >nul