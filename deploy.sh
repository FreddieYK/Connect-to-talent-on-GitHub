#!/bin/bash

echo "🚀 GitHub项目分析工具 - Vercel部署脚本"
echo "========================================"

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit: GitHub Analysis Tool"
    echo "✅ Git仓库初始化完成"
else
    echo "📁 Git仓库已存在"
fi

# 检查环境文件
if [ ! -f ".env" ]; then
    echo "⚙️  创建环境配置文件..."
    cp .env.example .env
    echo "✅ 请编辑.env文件配置您的API密钥"
else
    echo "⚙️  环境配置文件已存在"
fi

echo ""
echo "📋 接下来的步骤："
echo "1. 编辑.env文件，配置您的API密钥"
echo "2. 推送代码到GitHub仓库"
echo "3. 在Railway部署后端API"
echo "4. 在Vercel部署前端"
echo "5. 配置环境变量"
echo ""
echo "详细步骤请查看 DEPLOYMENT.md 文件"
echo ""
echo "🎉 准备工作完成！开始部署吧！"