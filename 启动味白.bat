@echo off
title 味白 · 个人工作台
echo ==============================
echo   味白 · 个人工作台 v1.0.0
echo ==============================
echo.
echo 正在启动服务...
echo.
pip install -r requirements.txt >nul 2>&1
start http://localhost:8000
python app.py
pause
