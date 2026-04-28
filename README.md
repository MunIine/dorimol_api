[![Frontend](https://img.shields.io/badge/Frontend-Flutter-1181a6?&logo=flutter&logoColor=white)](https://github.com/MunIine/dorimol) [![Python](https://img.shields.io/badge/Python-3.12-356fa0?&logo=python&logoColor=white)](https://www.python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-Backend-059487?&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-4481ae?&logo=postgresql&logoColor=white)](https://www.postgresql.org) 

# Dorimol API

Backend API онлайн-магазина для мобильного приложения Dorimol (Flutter).  
Сервис отвечает за авторизацию пользователей, каталог товаров, отзывы, оформление заказов и выдачу клиентской конфигурации.

## Ключевой функционал

- Авторизация через Firebase ID Token (`/auth/firebase`) с выдачей пары JWT (`access_token`, `refresh_token`).
- Проверка и обновление токенов (`/auth/validate`, `/auth/refresh`).
- Работа с профилем пользователя: чтение текущего профиля, обновление данных, загрузка аватара.
- Каталог: получение списка категорий и товаров с фильтрами/сортировкой, детальная карточка товара.
- Отзывы: получение отзывов по товару.
- Заказы: создание заказа, получение заказа по ID, история заказов пользователя.
- Ценообразование в заказах: расчет с учетом оптовой цены и персональной скидки пользователя.
- Клиентская конфигурация: получение ключ-значение настроек из БД (`/config/`).

## Технологический стек

- Язык: `Python 3`
- Web framework: `FastAPI`
- ORM / работа с БД: `SQLAlchemy` (async)
- База данных: `PostgreSQL`
- Миграции: `Alembic`
- Валидация и схемы: `Pydantic`
- Аутентификация:
  - внешний провайдер: `Firebase Admin SDK` (проверка ID token),
  - внутренние токены: `JWT` (`HS256`, bearer-схема)
- Обработка изображений: `Pillow` (аватары)
- Контейнеризация: `docker-compose` (поднят только PostgreSQL)

## Архитектура

```text
Dorimol_API/
├── app/
│   ├── endpoints/              # HTTP-роуты и DAO по доменам (auth, user, products, orders и др.)
│   ├── service/                # Бизнес-логика (user/token/image сервисы, user DAO)
│   ├── migration/              # Конфигурация и ревизии Alembic
│   ├── main.py                 # Точка входа FastAPI, подключение роутеров и статики
│   ├── config.py               # Загрузка настроек из .env
│   ├── database.py             # Инициализация async SQLAlchemy engine/session
│   ├── models.py               # ORM-модели (users, products, orders, ...)
│   ├── schema.py               # Pydantic-схемы запросов/ответов
│   ├── dependencies.py         # DI-зависимости FastAPI
│   ├── constants.py            # Константы домена (статусы, сортировки, скидки)
│   ├── dao.py                  # Базовый DAO
│   └── email.py                # Отправка email уведомлений о заказах
├── .env.example                # Пример переменных окружения
├── requirements.txt            # Python-зависимости
├── alembic.ini                 # Конфигурация Alembic
├── docker-compose.yml          # Контейнер PostgreSQL
├── LICENSE.md
└── README.md
```

## API

- Локальный базовый URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Формат авторизации защищенных методов:

```http
Authorization: Bearer <jwt_token>
```

### Группы эндпоинтов

#### Публичные (без JWT)

- Сервис:
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
- Статические файлы:
  - `GET /media/categories/*`
  - `GET /media/products/*`
  - `GET /media/avatars/*`

#### Приватные (требуется Bearer JWT)

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

## Содержимое таблицы config

| Ключ              | Возможное значение      | Назначение                                   |
| ----------------- | ----------------------- | -------------------------------------------- |
| `min_app_version` | `"x.x.x"`               | Минимальная поддерживаемая версия приложения |
| `maintenance_mode`| `bool`                  | Режим технического обслуживания              |
| `delivery_cities` | `list[str]`             | Города возможной доставки                    |

## Переменные окружения

Все переменные читаются из `.env` (см. `.env.example`).


| Переменная       | Назначение              |
| ---------------- | ----------------------- |
| `DB_USER`        | Пользователь PostgreSQL |
| `DB_PASSWORD`    | Пароль PostgreSQL       |
| `DB_HOST`        | Хост PostgreSQL         |
| `DB_PORT`        | Порт PostgreSQL         |
| `DB_NAME`        | Имя базы данных         |
| `EMAIL_API_KEY`  | API-ключ Mailgun        |
| `EMAIL_FROM`     | Email отправителя       |
| `EMAIL_TO`       | Email получателя        |
| `JWT_SECRET_KEY` | Секрет для подписи JWT  |


Дополнительно требуется файл `serviceAccountKey.json` в корне проекта для инициализации Firebase Admin SDK.

## Запуск локально

### 1) Подготовка окружения

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2) Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3) Настройка переменных окружения

```bash
cp .env.example .env
```

Заполните значения в `.env` и добавьте `serviceAccountKey.json`.

### 4) Запуск PostgreSQL

```bash
docker-compose up -d
```

### 5) Применение миграций

```bash
alembic upgrade head
```

### 6) Запуск API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Лицензия

Проект распространяется по лицензии **All Rights Reserved**. Подробные условия: `LICENCE.md`.