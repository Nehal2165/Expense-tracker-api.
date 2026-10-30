# Expense Tracker API

A beginner-friendly REST API for recording expenses, filtering records, and generating spending summaries. Built with **Python, FastAPI, SQLAlchemy, and SQLite**. The database URL can be configured to use PostgreSQL.

## Features

- Create, read, update, and delete expenses (CRUD)
- Validate titles, categories, dates, and positive monetary amounts
- Filter by category and date range
- Paginate expense lists with `limit` and `offset`
- Summarize total spending, expense count, and totals by category
- Interactive API docs through Swagger UI
- Automated tests with pytest
- Dockerfile included

## Tech stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Pydantic
- SQLite by default
- Pytest

## Run locally

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR-USERNAME/expense-tracker-api.git
   cd expense-tracker-api
   ```

2. Create and activate a virtual environment:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000/docs` in your browser to try the endpoints.

The SQLite database file `expenses.db` is created automatically when the app starts. It is excluded from Git by `.gitignore`.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| POST | `/expenses` | Create an expense |
| GET | `/expenses` | List expenses; optional category/date filters and pagination |
| GET | `/expenses/{expense_id}` | Get one expense |
| PUT | `/expenses/{expense_id}` | Update an expense |
| DELETE | `/expenses/{expense_id}` | Delete an expense |
| GET | `/summary` | Total amount, expense count, and category totals |

### Example request

`POST /expenses`

```json
{
  "title": "Groceries",
  "amount": "425.50",
  "category": "Food",
  "expense_date": "2026-10-30",
  "description": "Weekly groceries"
}
```

Example filters:

```text
GET /expenses?category=Food
GET /expenses?start_date=2026-10-01&end_date=2026-10-31
GET /expenses?limit=10&offset=0
GET /summary?start_date=2026-10-01&end_date=2026-10-31
```

## Run tests

```bash
pytest -q
```

## Docker

Build and run:

```bash
docker build -t expense-tracker-api .
docker run --rm -p 8000:8000 -v expense-data:/app/data expense-tracker-api
```

Note: the default database URL stores the SQLite file in the container working directory. For persistent Docker storage, set `DATABASE_URL=sqlite:////app/data/expenses.db` and mount `/app/data` to a volume.

## Database design

The `expenses` table contains:

- `id`: integer primary key
- `title`: short expense name
- `amount`: decimal monetary amount
- `category`: expense category
- `expense_date`: date of expense
- `description`: optional notes

## Possible improvements

- Add user accounts and JWT authentication
- Add database migrations with Alembic
- Add PostgreSQL integration tests
- Add CI with GitHub Actions
- Deploy the API and add a live demo

## Scope and limitations

This starter version does not include user accounts or authentication. Do not use it to store sensitive personal financial data. It is intended as a learning project.

## License

MIT
