# Finance Tracker API

A REST API for tracking personal income and expenses, built with FastAPI. Powers the Finance Tracker React frontend.

**Live API:** https://finance-tracker-api-qsu8.onrender.com  
**Frontend:** https://finance-tracker-sigma-three.vercel.app/

## Endpoints

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions` | List all transactions |
| POST | `/transactions` | Add a new transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |

### Summary
| Method | Endpoint | Description |
|---|---|---|
| GET | `/summary` | Total income, expenses, balance, and spending by category |

## Tech Stack

- Python 3 / FastAPI
- SQLite via SQLAlchemy (PostgreSQL in production)
- Pydantic for request validation
- CORS enabled for frontend connection
- Deployed on Render

## Getting Started

### 1. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### 2. Run the server

```bash
python -m uvicorn main:app --reload
```

### 3. Open interactive docs

```
http://127.0.0.1:8000/docs
```

## Deployment

Deployed on Render. Environment variables required:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (set automatically by Render) |

## Project Structure

```
backend/
├── main.py          # FastAPI app, routes, models, database
├── Procfile         # Gunicorn + uvicorn worker config
└── requirements.txt # Python dependencies
```
