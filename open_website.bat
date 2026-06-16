@echo off
cd /d "%~dp0"
set DEBUG=True
echo.
echo ==========================================
echo RRV furniture ^& aluminum workers
echo ==========================================
echo.
echo Preparing database and admin account...
python manage.py migrate
python manage.py setup_rrv_admin
echo.
echo Website ready. Opening in browser...
echo.
echo Login:  http://127.0.0.1:8000/accounts/login/
echo Public: http://127.0.0.1:8000/catalog/
echo Admin:  http://127.0.0.1:8000/admin/
echo.
echo Username: rajesh
echo Email:    rajesh@rrvfurniture.local
echo Password: vikas^&rakesh
echo.
start "" "http://127.0.0.1:8000/accounts/login/"
python manage.py runserver 127.0.0.1:8000
pause
