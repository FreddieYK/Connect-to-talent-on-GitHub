@echo off
chcp 65001 >nul
title 创建GitHub手动上传包

echo.
echo ==========================================
echo        创建 GitHub 手动上传包
echo     包含Railway端口修复的最新版本
echo ==========================================
echo.

cd /d "%~dp0"

:: 设置上传包目录
set UPLOAD_DIR=GitHub_Manual_Upload
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo [1/5] 🗂️  准备上传包目录...
if exist "%UPLOAD_DIR%" (
    echo 清理旧的上传包...
    rmdir /s /q "%UPLOAD_DIR%"
)

mkdir "%UPLOAD_DIR%"
echo ✅ 上传包目录准备完成

echo.
echo [2/5] 📋 复制核心项目文件...

:: 复制核心Python文件
copy "main.py" "%UPLOAD_DIR%\" >nul
copy "models.py" "%UPLOAD_DIR%\" >nul
copy "github_crawler.py" "%UPLOAD_DIR%\" >nul
copy "requirements.txt" "%UPLOAD_DIR%\" >nul
copy "frontend_server.py" "%UPLOAD_DIR%\" >nul

:: 复制Railway配置文件（包含端口修复）
copy "railway.json" "%UPLOAD_DIR%\" >nul
copy "Procfile" "%UPLOAD_DIR%\" >nul

:: 复制Vercel配置
copy "vercel.json" "%UPLOAD_DIR%\" >nul

:: 复制环境配置
if exist ".env.example" copy ".env.example" "%UPLOAD_DIR%\" >nul

echo ✅ 核心文件复制完成

echo.
echo [3/5] 🌐 复制前端静态文件...

:: 创建静态文件目录
mkdir "%UPLOAD_DIR%\static"

:: 复制前端文件
copy "static\index.html" "%UPLOAD_DIR%\static\" >nul
copy "static\script.js" "%UPLOAD_DIR%\static\" >nul
copy "static\styles.css" "%UPLOAD_DIR%\static\" >nul

echo ✅ 前端文件复制完成

echo.
echo [4/5] 📚 复制文档和脚本...

:: 复制说明文档
copy "README.md" "%UPLOAD_DIR%\" >nul
copy "DEPLOYMENT.md" "%UPLOAD_DIR%\" >nul
copy "Railway部署指南.md" "%UPLOAD_DIR%\" >nul
copy "Railway环境变量配置问题解决.md" "%UPLOAD_DIR%\" >nul

:: 复制工具脚本
copy "启动工具.bat" "%UPLOAD_DIR%\" >nul
copy "更新Vercel部署.bat" "%UPLOAD_DIR%\" >nul

:: 创建.gitignore
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo env/
echo venv/
echo .venv/
echo .env
echo pip-log.txt
echo pip-delete-this-directory.txt
echo .DS_Store
echo Thumbs.db
echo *.log
echo node_modules/
echo GitHub_Manual_Upload/
echo GitHub_Upload_Package/
) > "%UPLOAD_DIR%\.gitignore"

echo ✅ 文档和脚本复制完成

echo.
echo [5/5] 📊 生成上传说明...

:: 创建上传说明文件
(
echo # GitHub 手动上传说明
echo.
echo ## 📦 本上传包包含内容
echo.
echo ### 🔧 核心文件 ^(已修复Railway端口问题^)
echo - main.py              # FastAPI主应用
echo - models.py            # 数据模型
echo - github_crawler.py    # GitHub爬虫
echo - requirements.txt     # Python依赖
echo - frontend_server.py   # 前端服务器
echo.
echo ### ⚙️  部署配置文件
echo - railway.json         # Railway部署配置 ^(修复端口错误^)
echo - Procfile            # 进程定义文件
echo - vercel.json         # Vercel部署配置
echo - .env.example        # 环境变量示例
echo - .gitignore          # Git忽略文件
echo.
echo ### 🌐 前端文件
echo - static/index.html   # 主页面
echo - static/script.js    # 前端逻辑 ^(包含静态演示修复^)
echo - static/styles.css   # 样式文件
echo.
echo ### 📚 文档和工具
echo - README.md                              # 项目说明
echo - DEPLOYMENT.md                          # 部署指南
echo - Railway部署指南.md                      # Railway详细指南
echo - Railway环境变量配置问题解决.md           # 问题解决方案
echo - 启动工具.bat                           # 本地启动脚本
echo - 更新Vercel部署.bat                     # Vercel更新脚本
echo.
echo ## 🚀 上传步骤
echo.
echo ### 方式1：GitHub仓库直接更新（推荐）
echo 1. **访问GitHub仓库**
echo    https://github.com/FreddieYK/Connect-to-talent-on-GitHub
echo.
echo 2. **直接编辑文件**
echo    - 点击要修改的文件，如railway.toml
echo    - 点击编辑按钮（铅笔图标）
echo    - 修改内容后点击"Commit changes"
echo    - Railway会自动检测并重新部署
echo.
echo ### 方式2：批量文件上传（大量更改时）
echo 1. **删除旧文件**
echo    - 点击仓库中的文件，然后点击删除按钮
echo    - 或者选择 "Upload files" 直接覆盖
echo.
echo 2. **上传新文件**
echo    - 点击 "Upload files" 按钮
echo    - 将本文件夹中的所有文件拖拽到上传区域
echo    - 或者点击 "choose your files" 选择文件
echo.
echo 3. **提交更改**
echo    - 输入提交信息：^"fix: 修复Railway端口配置错误和CORS问题^"
echo    - 点击 "Commit changes"
echo.
echo ## 🔧 重要修复说明
echo.
echo ### ✅ Railway端口错误修复
echo - 修复了 'Invalid value for --port: $PORT' 错误
echo - railway.json 使用 ^${PORT:-8000} 语法
echo - Procfile 同样使用正确的端口配置
echo.
echo ### ✅ Vercel静态部署优化
echo - 添加了静态演示模式
echo - 修复了CORS和API连接问题
echo - 优化了用户体验和错误提示
echo.
echo ### ✅ 文档完善
echo - 更新了Railway部署指南
echo - 添加了环境变量配置问题解决方案
echo - 完善了故障排除文档
echo.
echo ## 📅 创建时间
echo %date% %time%
echo.
echo ---
echo 上传完成后，Railway将自动检测更改并重新部署。
echo 预计3-5分钟后修复生效。
) > "%UPLOAD_DIR%\UPLOAD_README.md"

echo ✅ 上传说明生成完成

:: 统计文件数量
set FILE_COUNT=0
for /r "%UPLOAD_DIR%" %%f in (*.*) do set /a FILE_COUNT+=1

echo.
echo ==========================================
echo ✅ GitHub手动上传包创建完成！
echo ==========================================
echo.
echo 📁 上传包位置: %CD%\%UPLOAD_DIR%
echo 📊 包含文件数: %FILE_COUNT% 个文件
echo 📝 上传说明: %UPLOAD_DIR%\UPLOAD_README.md
echo.
echo 🚀 修复内容摘要:
echo   ✅ Railway端口配置错误修复
echo   ✅ Vercel静态演示功能优化  
echo   ✅ CORS和API连接问题解决
echo   ✅ 完整的文档和工具脚本
echo.
echo 📋 下一步操作:
echo   1. 打开 %UPLOAD_DIR% 文件夹
echo   2. 阅读 UPLOAD_README.md 了解详细上传步骤
echo   3. 访问 GitHub 仓库进行手动上传
echo   4. 等待 Railway 自动重新部署
echo.

echo 🌍 正在打开上传包文件夹...
start "" "%CD%\%UPLOAD_DIR%"

echo.
echo 按任意键关闭窗口...
pause >nul