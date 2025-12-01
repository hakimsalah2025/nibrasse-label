@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║           ⏹️  إيقاف تطبيق NIBRASSE - نبــراس                 ║
echo ║           Stopping NIBRASSE Application                      ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1/2] البحث عن عمليات التطبيق...
echo       Searching for application processes...
echo.

REM البحث عن عمليات uvicorn
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul

if %errorlevel% neq 0 (
    echo ℹ️  لم يتم العثور على عمليات Python قيد التشغيل
    echo    No Python processes found running
    echo.
    echo ✅ التطبيق متوقف بالفعل
    echo    Application is already stopped
    pause
    exit /b 0
)

REM إيقاف جميع عمليات uvicorn (python)
echo [2/2] إيقاف التطبيق...
echo       Stopping the application...
echo.

REM محاولة إيقاف uvicorn بشكل محدد
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *uvicorn*" ^| find /I "python.exe"') do (
    echo 🔄 إيقاف العملية %%i...
    taskkill /PID %%i /F >nul 2>&1
)

REM إيقاف جميع عمليات Python التي تحتوي على uvicorn في سطر الأوامر
wmic process where "name='python.exe' and CommandLine like '%%uvicorn%%'" delete >nul 2>&1

REM التحقق من النتيجة
timeout /t 2 /nobreak >nul

tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" | find /I "uvicorn" >nul

if %errorlevel% equ 0 (
    echo.
    echo ⚠️  تحذير: قد تكون بعض العمليات ما زالت تعمل
    echo    Warning: Some processes may still be running
    echo.
    echo 💡 نصيحة: يمكنك إغلاق نوافذ Terminal يدوياً
    echo    Tip: You can manually close Terminal windows
) else (
    echo.
    echo ✅ تم إيقاف التطبيق بنجاح
    echo    Application stopped successfully
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║  📝 ملاحظة: إذا كان التطبيق يعمل في نافذة أخرى،            ║
echo ║     استخدم Ctrl+C في تلك النافذة لإيقافه                    ║
echo ║                                                               ║
echo ║  Note: If the app runs in another window,                    ║
echo ║  use Ctrl+C in that window to stop it                        ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

pause
