# Dorimol API

Backend REST API сервис для проекта Dorimol. Разработан на Python фреймворке FastAPI с использованием PostgreSQL. 


---

## Технологии
*   **Язык:** Python 3
*   **Фреймворк:** FastAPI
*   **Миграции:** Alembic
*   **База данных:** PostgreSQL
*   **Инструменты:** Docker, SQLAlchemy

---

## Структура проекта
```text
dorimol_api/
├── app/               # Основной код приложения
│   ├── migrations/    # Миграции Alembic
│   ├── config.py      # Конфигурация параметров с .env
│   ├── database.py    # Описание типов данных
│   ├── models.py      # Модели базы данных
│   ├── schema.py      # Схемы Pydantic 
│   └── main.py        # Точка входа
├── alembic.ini        # Конфигурация Alembic
├── requirements.txt   # Зависимости Python
├── docker-compose.yml # Конфигурация Docker для PostgreSQL
├── .env.example       # Пример файла с переменными окружения
├── LICENSE.md         # Лицензия
└── README.md          # Документация
```

---
## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
Создайте файл `.env` в корне проекта по примеру из `.env.example`

### 3. Запуск контейнера PostgreSQL
```bash
docker-compose up -d
```
### 4. Применение миграций
```bash
alembic upgrade head
```

### 5. Запуск приложения
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Документация API
После запуска приложения, автоматическая документация API будет доступна по адресу: 
`http://localhost:8000/docs`

## Список эндпоинтов
- `GET /` — Главная страница
- `GET /config/` — Получить файл конфигурации client
- `GET /categories/` — Получить список категорий
- `GET /products/` — Получить товары по фильтру
- `GET /products/{id}` — Получить полную информацию о товаре по id
- `GET /feedbacks/{product_id}` — Получить отзывы по id продукта
- `POST /orders/add` — Добавить новый заказ

## Лицензия
Этот проект лицензирован лицензией MIT. Подробности см. в файле [LICENSE.md](LICENSE.md)