@echo off
cd /d "%~dp0"
set DEBUG=True
echo.
echo RRV furniture ^& aluminum workers
echo Starting local website...
echo.
python manage.py migrate
python manage.py setup_rrv_admin
echo.
echo Login URL:   http://127.0.0.1:8000/accounts/login/
echo Public URL:  http://127.0.0.1:8000/catalog/
echo Admin URL:   http://127.0.0.1:8000/admin/
echo.
start "" "http://127.0.0.1:8000/accounts/login/"
python manage.py runserver 127.0.0.1:8000
pause
