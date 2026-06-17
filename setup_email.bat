@echo off
cd /d "%~dp0"
echo.
echo Configure OTP email SMTP
echo.
set /p EMAIL_USER=Enter Gmail address:
set /p EMAIL_PASS=Enter Gmail App Password:
(
echo EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo EMAIL_USE_TLS=True
echo EMAIL_HOST_USER=%EMAIL_USER%
echo EMAIL_HOST_PASSWORD=%EMAIL_PASS%
echo DEFAULT_FROM_EMAIL=RRV furniture ^& aluminum workers ^<%EMAIL_USER%^>
) > .env
echo.
echo Email settings saved to .env
echo Restart open_website.bat after this.
pause
