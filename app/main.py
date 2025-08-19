from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.products.router import router as router_products
from app.categories.router import router as router_categories
from app.feedbacks.router import router as router_feedbacks
from app.orders.router import router as router_orders
from app.configs.router import router as router_configs

app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "Сервер работает!"}


app.include_router(router_products)
app.include_router(router_categories)
app.include_router(router_feedbacks)
app.include_router(router_orders)
app.include_router(router_configs)

app.mount("/media/categories", StaticFiles(directory="media/categories/"), name="categories")
app.mount("/media/products", StaticFiles(directory="media/products/"), name="products")



### ДЛЯ DEBUG ЧЕРЕЗ БРАУЗЕР
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # или ["http://localhost:3000"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )