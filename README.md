[![Frontend](https://img.shields.io/badge/Frontend-Flutter-1181a6?&logo=flutter&logoColor=white)](https://github.com/MunIine/dorimol) [![Python](https://img.shields.io/badge/Python-3.12-356fa0?&logo=python&logoColor=white)](https://www.python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-Backend-059487?&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-4481ae?&logo=postgresql&logoColor=white)](https://www.postgresql.org) 

# Dorimol API
 
Backend API for the Dorimol (Flutter) mobile e-commerce app.  
The service handles user authentication, product catalog, reviews, order processing, and client configuration delivery.
 
## Key Features
 
- Authentication via Firebase ID Token (`/auth/firebase`) with JWT pair issuance (`access_token`, `refresh_token`).
- Token validation and refresh (`/auth/validate`, `/auth/refresh`).
- User profile management: read current profile, update data, upload avatar.
- Catalog: fetch categories and products with filters/sorting, detailed product card.
- Reviews: fetch reviews by product.
- Orders: create an order, get order by ID, user order history.
- Order pricing: calculation based on wholesale price and personal user discount.
- Client configuration: fetch key-value settings from the DB (`/config/`).
## Tech Stack
 
- Language: `Python 3`
- Web framework: `FastAPI`
- ORM / database: `SQLAlchemy` (async)
- Database: `PostgreSQL`
- Migrations: `Alembic`
- Validation & schemas: `Pydantic`
- Authentication:
  - External provider: `Firebase Admin SDK` (ID token verification)
  - Internal tokens: `JWT` (`HS256`, bearer scheme)
- Image processing: `Pillow` (avatars)
- Containerization: `docker`

## Architecture

```text
Dorimol_API/
├── app/
│   ├── endpoints/              # HTTP routes and DAOs by domain (auth, user, products, orders, etc.)
│   ├── service/                # Business logic (user/token/image services, user DAO)
│   ├── migration/              # Alembic configuration and revisions
│   ├── main.py                 # FastAPI entry point, router and static file registration
│   ├── config.py               # Settings loader from .env
│   ├── database.py             # Async SQLAlchemy engine/session initialization
│   ├── models.py               # ORM models (users, products, orders, ...)
│   ├── schema.py               # Pydantic request/response schemas
│   ├── dependencies.py         # FastAPI DI dependencies
│   ├── constants.py            # Domain constants (statuses, sorting, discounts)
│   ├── dao.py                  # Base DAO
│   └── email.py                # Order notification emails
├── nginx/
│   └── nginx.conf              # Nginx configuration
├── .env.example                # Environment variables example
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Container
├── Dockerfile                  # FastAPI application image
├── LICENSE.md
└── README.md
```

## API
 
- Base dev URL: `http://localhost:8000`
- Base full docker stack URL: `http://localhost`
- Swagger UI: `http://localhost/docs` (or `:8000/docs` in local dev)
- Authorization format for protected endpoints:
  ```http
  Authorization: Bearer <jwt_token>
  ```

### Endpoint Groups
 
#### Public (no JWT required)
 
- Service:
  - `GET /`
- Auth:
  - `POST /auth/firebase`
- Products / Categories / Feedbacks:
  - `GET /products/`
  - `GET /products/{id}`
  - `GET /categories/`
  - `GET /feedbacks/{product_id}`
- Config:
  - `GET /config/`
- Static files:
  - `GET /media/categories/*`
  - `GET /media/products/*`
  - `GET /media/avatars/*`
#### Private (Bearer JWT required)
 
- Auth:
  - `POST /auth/refresh`
  - `GET /auth/validate`
- User:
  - `PATCH /user/update`
  - `POST /user/update/avatar`
  - `GET /user/me`
  - `GET /user/me/orders`
- Orders:
  - `POST /orders/add`
  - `GET /orders/{order_id}`

## Config Table Contents

| Key               | Example Value           | Description                                  |
| ----------------- | ----------------------- | -------------------------------------------- |
| `min_app_version` | `"x.x.x"`               | Minimum supported app version                |
| `maintenance_mode`| `bool`                  | Maintenance mode flag                        |
| `delivery_cities` | `list[str]`             | Cities available for delivery                |

## Environment Variables
 
All variables are read from `.env` (see `.env.example`).
 
| Variable         | Description             |
| ---------------- | ----------------------- |
| `DB_USER`        | PostgreSQL user         |
| `DB_PASSWORD`    | PostgreSQL password     |
| `DB_HOST`        | PostgreSQL host*        |
| `DB_PORT`        | PostgreSQL port**       |
| `DB_NAME`        | Database name           |
| `EMAIL_API_KEY`  | Mailgun API key         |
| `EMAIL_FROM`     | Sender email address    |
| `EMAIL_TO`       | Recipient email address |
| `JWT_SECRET_KEY` | JWT signing secret      |
 
 \* `localhost` for local dev, `postgres` when running the API in Docker
 ** `5433` for local dev (mapped), `5432` when running the API in Docker

Additionally, a `serviceAccountKey.json` file is required in the project root for Firebase Admin SDK initialization.

## Running the Project

There are two ways to run this project: locally with only the database in Docker (faster iteration for development), or fully containerized (full docker stack)

### Local development
 
#### 1) Set up the environment

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

#### 2) Install dependencies

```bash
pip install -r requirements.txt
```

#### 3) Configure environment variables

```bash
cp .env.example .env
```

Fill in the values in `.env` and add `serviceAccountKey.json`.
 
#### 4) Start PostgreSQL

```bash
docker compose up -d postgres
```

#### 5) Apply migrations

```bash
alembic upgrade head
```

#### 6) Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

##### The API is now available on: http://localhost:8000

### Full Docker Stack

#### 1) Build and start all services

```bash
docker compose up --build -d
```

####  2) Apply migrations

```bash
docker compose exec api alembic upgrade head
```

##### The API is now available through Nginx: http://localhost

## License
 
The project is distributed under the **All Rights Reserved** license. Full terms: `LICENSE.md`.