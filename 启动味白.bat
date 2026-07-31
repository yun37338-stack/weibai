@echo off
chcp 65001 >nul
title 味白 · 个人工作台

echo ===============================
echo   味白 · 个人工作台 启动中...
echo ===============================
echo.

cd /d "%~dp0"

echo [1/2] 检查并安装 Python 依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo 依赖安装失败，请确认已安装 Python 并添加到 PATH
    pause
    exit /b 1
)

echo [2/2] 启动服务...
echo.
echo 服务已启动！浏览器即将打开...
echo 访问地址: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8000

python app.py
pause
