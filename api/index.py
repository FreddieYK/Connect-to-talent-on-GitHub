import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app

# Vercel需要这个handler函数
handler = app