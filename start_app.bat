@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║           🚀 تشغيل تطبيق NIBRASSE - نبــراس                  ║
echo ║        Starting NIBRASSE Application                         ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM التحقق من وجود Python
echo [1/4] التحقق من تثبيت Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ خطأ: Python غير مثبت على النظام
    echo ❌ Error: Python is not installed
    echo 📥 يرجى تثبيت Python 3.10 أو أحدث من: https://www.python.org/
    pause
    exit /b 1
)
echo ✅ Python متوفر
echo.

REM التحقق من وجود مجلد backend
echo [2/4] التحقق من مجلد المشروع...
if not exist "backend" (
    echo ❌ خطأ: مجلد backend غير موجود
    echo ❌ Error: backend folder not found
    pause
    exit /b 1
)
echo ✅ مجلد backend موجود
echo.

REM التحقق من وجود ملف .env
echo [3/4] التحقق من الإعدادات...
if not exist "backend\.env" (
    echo ⚠️  تحذير: ملف .env غير موجود
    echo ⚠️  Warning: .env file not found
    echo 📝 سيتم استخدام الإعدادات الافتراضية
    echo.
)

REM تشغيل الخادم
echo [4/4] تشغيل الخادم...
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║  🌐 التطبيق سيفتح على: http://localhost:8000                ║
echo ║     The app will open at: http://localhost:8000              ║
echo ║                                                               ║
echo ║  ⏹️  لإيقاف التطبيق: اضغط Ctrl+C أو شغّل stop_app.bat       ║
echo ║     To stop: Press Ctrl+C or run stop_app.bat                ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM الانتقال لمجلد backend
cd backend

REM فتح المتصفح بعد 3 ثواني (في الخلفية)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8000"

REM تشغيل uvicorn
echo 🚀 جاري بدء التشغيل...
echo 💡 انتظر حتى ترى "Application startup complete"
echo 🌐 سيتم فتح المتصفح تلقائياً خلال 3 ثواني...
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM في حالة توقف الخادم
echo.
echo ⏹️  تم إيقاف التطبيق
echo    Application stopped
pause
