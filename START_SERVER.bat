@echo off
echo ========================================
echo StoreVision Analytics Platform
echo Production-Ready CCTV Intelligence System
echo ========================================
echo.

cd backend

echo Starting server...
echo.
echo Dashboard: http://localhost:8000/static/index.html
echo API Docs:  http://localhost:8000/docs
echo Health:    http://localhost:8000/health
echo.

python main.py
