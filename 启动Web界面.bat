@echo off
echo ========================================
echo 保险智能助手 Web界面
echo ========================================
echo.
echo 正在启动服务器...
echo.

cd /d "%~dp0"
streamlit run app.py --server.port 8501 --server.address localhost

pause
