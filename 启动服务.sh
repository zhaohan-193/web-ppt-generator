#!/bin/bash
echo "========================================"
echo "  SlideForge 演示文稿生成平台 - 启动"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

echo "[1/3] 安装依赖..."
pip3 install fastapi uvicorn jinja2 python-multipart -q 2>/dev/null || \
python3 -m pip install fastapi uvicorn jinja2 python-multipart -q

echo "[2/3] 启动服务..."
echo ""
echo "========================================"
echo "  启动成功！请在浏览器中打开:"
echo ""
echo "  http://localhost:8000"
echo ""
echo "  按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
