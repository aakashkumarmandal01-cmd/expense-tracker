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

## 3. Database

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

## 4. Multi-user privacy

Every private record has `user_id`.

Database operations always use the authenticated user's ID. The UI never loads all users' transactions and filters them only in the browser.

Passwords are stored as bcrypt hashes.

AI receives only the current user's transaction/profile data.

## 5. Adding a category

Edit:

`utils/helpers.py`

Add a sub-category under an existing parent, for example:

```python
"Food": ["College Canteen", "New Food Type"]
```

For a completely custom category, the budget screen accepts a custom category name. A future production version can expose a full category-management screen.

## 6. Backup

For SQLite development, use Settings → Create SQLite backup.

For production PostgreSQL/Supabase, use scheduled database backups/snapshots provided by your database provider.

## 7. Important production hardening

Before public deployment:

- Put Streamlit behind HTTPS.
- Use PostgreSQL/Supabase rather than SQLite.
- Add a production email/password-reset service.
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
