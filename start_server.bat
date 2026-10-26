
@echo off
cd /d "C:\AI CUSTOMER CHATBOT"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Project virtual environment not found.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m uvicorn main:app --reload

pause
