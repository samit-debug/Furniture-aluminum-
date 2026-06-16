# RRV furniture & aluminum workers

Django based management system for aluminum and furniture workshop records.

## Modules

- Login and Django Admin roles
- Email or username based login
- Dashboard with order, sales, payment, and low-stock metrics
- Business settings for shop name, owner, contact, GST, and logo
- Customer management with order history and pending payment
- Product management with image upload, featured flag, and website visibility
- Public product catalog controlled from admin/product page
- Order management with measurement, status, payment, and bill links
- Measurement auto calculation for area and material requirement
- Stock management with low-stock alert
- Worker management and work assignment
- Billing with print/PDF-ready invoice page
- Payment records for cash, UPI, bank transfer, and cheque
- Reports snapshot and saved report notes

## Run Locally

Easy way on Windows:

1. Double-click `open_website.bat`.
2. Keep the command window open.
3. Chrome/browser will open the login page automatically.

Manual way:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py setup_rrv_admin
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Default admin:

- Username: `rajesh`
- Email: `samitkumarrai948@gmail.com`
- Email alias: `rajesh@rrvfurniture.local`
- Password: `vikas&rakesh`

Public catalog:

- `http://127.0.0.1:8000/catalog/`

Important local URLs:

- Login: `http://127.0.0.1:8000/accounts/login/`
- Admin panel: `http://127.0.0.1:8000/admin/`
- Public website: `http://127.0.0.1:8000/catalog/`

Forgot password:

- Open `http://127.0.0.1:8000/accounts/password_reset/`
- Enter `samitkumarrai948@gmail.com`
- In local development, the reset link is shown on the next page.
- On Render/live hosting, configure SMTP environment variables so reset links go by email.

## Roles

Create users and groups from Django Admin:

- Admin: full admin access
- Staff: customer, order, bill, and payment work
- Worker: link the user to a Worker profile; order and assignment lists are scoped to assigned work

## Render Deployment

This project includes `render.yaml` for Render Blueprint deployment.

1. Push this project to GitHub.
2. Open Render Dashboard.
3. Create a new Blueprint and select the GitHub repository.
4. Render will create the web service and PostgreSQL database.
5. The pre-deploy command runs migrations and creates the `rajesh` admin account.
6. After deployment, open the service URL and login with the admin account.

Important environment variables:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
