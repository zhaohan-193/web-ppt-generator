@echo off
chcp 65001 >nul
echo ========================================
echo   SlideForge 演示文稿生成平台 - 启动
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 未检测到 Python，请先安装 Python 3.10+
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

echo [1/3] 安装依赖...
%PYTHON% -m pip install fastapi uvicorn jinja2 python-multipart -q

echo [2/3] 启动服务...
echo.
echo ========================================
echo   启动成功！请在浏览器中打开:
echo.
echo   http://localhost:8000
echo.
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

%PYTHON% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
