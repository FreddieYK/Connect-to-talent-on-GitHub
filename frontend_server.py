#!/usr/bin/env python3
"""
前端开发服务器 - 运行在3000端口
提供静态文件服务和热重载功能
作者: GitHub 爬虫工具团队
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path
import mimetypes
import urllib.parse

# 设置端口和静态文件目录
PORT = 3000
STATIC_DIR = Path(__file__).parent / "static"

class StaticFileHandler(http.server.SimpleHTTPRequestHandler):
    """处理静态文件的HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)
    
    def end_headers(self):
        # 添加CORS头，允许跨域请求到后端API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def guess_type(self, path):
        """根据文件扩展名猜测MIME类型"""
        mimetype, encoding = mimetypes.guess_type(path)
        
        # 确保路径是字符串类型
        path_str = str(path)
        
        # 确保JavaScript文件返回正确的MIME类型
        if path_str.endswith('.js'):
            return 'application/javascript'
        elif path_str.endswith('.css'):
            return 'text/css'
        elif path_str.endswith('.html'):
            return 'text/html'
        elif path_str.endswith('.json'):
            return 'application/json'
        
        return mimetype or 'application/octet-stream'
    
    def do_GET(self):
        """处理GET请求"""
        # 解析URL路径
        parsed_path = urllib.parse.urlparse(self.path)
        clean_path = parsed_path.path
        
        # 移除查询参数（如?v=local-1）
        if clean_path.startswith('/'):
            clean_path = clean_path[1:]
        
        # 如果是根路径，返回index.html
        if not clean_path or clean_path == '/':
            clean_path = 'index.html'
        
        # 构建完整文件路径
        file_path = STATIC_DIR / clean_path
        
        print(f"请求路径: {self.path} -> {clean_path} -> {file_path}")
        
        try:
            # 检查文件是否存在
            if file_path.exists() and file_path.is_file():
                # 读取文件内容
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # 设置响应状态码
                self.send_response(200)
                
                # 设置Content-Type
                content_type = self.guess_type(str(file_path))
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                
                # 添加缓存控制（开发环境不缓存）
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                self.end_headers()
                
                # 发送文件内容
                self.wfile.write(content)
                
                print(f"✅ 成功返回文件: {file_path} ({content_type})")
                
            else:
                # 文件不存在，对于SPA应用返回index.html
                print(f"⚠️ 文件不存在: {file_path}，返回index.html")
                
                index_path = STATIC_DIR / 'index.html'
                if index_path.exists():
                    with open(index_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Content-Length', str(len(content)))
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_error(404, "File not found")
                    
        except Exception as e:
            print(f"❌ 处理请求时出错: {e}")
            self.send_error(500, f"Internal server error: {e}")

def start_frontend_server():
    """启动前端开发服务器"""
    try:
        # 检查静态文件目录是否存在
        if not STATIC_DIR.exists():
            print(f"❌ 静态文件目录不存在: {STATIC_DIR}")
            return False
        
        # 检查index.html是否存在
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            print(f"❌ 找不到index.html文件: {index_file}")
            return False
        
        # 检查script.js是否存在
        script_file = STATIC_DIR / "script.js"
        if not script_file.exists():
            print(f"❌ 找不到script.js文件: {script_file}")
            return False
        
        print(f"📁 静态文件目录: {STATIC_DIR}")
        print(f"📄 index.html: {index_file} ({'存在' if index_file.exists() else '不存在'})")
        print(f"📄 script.js: {script_file} ({'存在' if script_file.exists() else '不存在'})")
        
        # 创建服务器
        with socketserver.TCPServer(("", PORT), StaticFileHandler) as httpd:
            print(f"🚀 前端开发服务器启动成功!")
            print(f"📱 访问地址: http://localhost:{PORT}")
            print(f"🔧 后端API地址: http://localhost:8000")
            print("按 Ctrl+C 停止服务器")
            print("-" * 50)
            
            # 自动打开浏览器
            webbrowser.open(f'http://localhost:{PORT}')
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 10048:  # Windows端口被占用
            print(f"❌ 端口 {PORT} 已被占用，请先关闭占用该端口的程序")
        else:
            print(f"❌ 启动服务器失败: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n✅ 前端服务器已停止")
        return True
    except Exception as e:
        print(f"❌ 服务器运行出错: {e}")
        return False

if __name__ == "__main__":
    start_frontend_server()