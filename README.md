# 🎓 College Expense Tracker & Personal Finance Dashboard

A modular Streamlit personal-finance application designed for college students living away from home.

## Features

- Multi-user registration/login with bcrypt password hashing
- Strict user-scoped database queries
- SQLite for local development
- PostgreSQL/Supabase support for production
- Income and expense tracking
- College-specific categories
- Analytics and Plotly charts
- Monthly budgets and warnings
- Savings goals
- Recurring expenses
- Trip expense tracking
- AI finance assistant
- Automatic insights
- Demo data
- CSV export
- SQLite backup
- Account deletion
- Modular architecture

## 1. Run in VS Code

Open the project folder in VS Code.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

## 2. Add AI API key

Open `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6-mini
```

Never commit `.env`.

If no API key is configured, the app still works and uses deterministic local calculations for common finance questions.

## 3. Configure email password reset

The login page includes a working email-based password-reset flow. It uses a random, single-use token, stores only the token hash in the database, and expires the link after 30 minutes.

Add these values to Streamlit Community Cloud → Manage app → Settings → Secrets (TOML format):

```toml
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_google_app_password"
SMTP_FROM = "your_email@gmail.com"
APP_URL = "https://your-app-name.streamlit.app"
```

For local development, add the same keys to `.env`. `APP_URL` must be the public URL of your deployed app, without a trailing slash. For Gmail, enable 2-Step Verification and create an App Password; do not use your normal Google password. You can use another SMTP provider by substituting its host, port, login, and sender details.

After deploying these code changes, `init_db()` creates the `password_reset_tokens` table automatically. A reset request displays a generic response so the app does not reveal whether an email is registered. The reset link expires in 30 minutes and is single-use.

## 4. Database

### Local development

SQLite is automatic:

`data/expenses.db`

The database is created on first launch.

### Production

Set a PostgreSQL/Supabase connection string in `.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

The application will use PostgreSQL instead of SQLite.

For 10, 100, or 1,000+ users, use PostgreSQL/Supabase, HTTPS, a proper deployment platform, backups, and rate limiting.

## 5. Multi-user privacy

Every private record has `user_id`.

Database operations always use the authenticated user's ID. The UI never loads all users' transactions and filters them only in the browser.

Passwords are stored as bcrypt hashes.

AI receives only the current user's transaction/profile data.

## 6. Adding a category

Edit:

`utils/helpers.py`

Add a sub-category under an existing parent, for example:

```python
"Food": ["College Canteen", "New Food Type"]
```

For a completely custom category, the budget screen accepts a custom category name. A future production version can expose a full category-management screen.

## 7. Backup

For SQLite development, use Settings → Create SQLite backup.

For production PostgreSQL/Supabase, use scheduled database backups/snapshots provided by your database provider.

## 8. Important production hardening

Before public deployment:

- Put Streamlit behind HTTPS.
- Use PostgreSQL/Supabase rather than SQLite.
- Add rate limiting to login and password-reset requests and monitor email-sending failures.
- Add CSRF/session hardening appropriate to the hosting architecture.
- Add rate limiting.
- Store secrets only in environment variables/secret storage.
- Restrict database credentials.
- Configure automated database backups.
- Review AI data-retention/privacy settings for the chosen provider.
- Do not expose admin endpoints to normal users.

## Project structure

```text
college_expense_tracker/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── database/
│   ├── database.py
│   └── schema.sql
├── modules/
│   ├── ai_assistant.py
│   ├── analytics.py
│   ├── auth.py
│   ├── budgets.py
│   ├── dashboard.py
│   ├── forecasting.py
│   ├── onboarding.py
│   ├── recurring.py
│   ├── savings.py
│   ├── settings.py
│   ├── transactions.py
│   └── trips.py
├── utils/
│   ├── calculations.py
│   ├── formatting.py
│   └── helpers.py
└── data/
    └── expenses.db
```

## Notes

This is a complete functional starter suitable for local development and extension. Production authentication can be strengthened further with a managed identity provider or hardened server-side session/cookie architecture.
