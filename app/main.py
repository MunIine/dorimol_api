from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from fastapi.staticfiles import StaticFiles
from app.endpoints.products.router import router as router_products
from app.endpoints.categories.router import router as router_categories
from app.endpoints.feedbacks.router import router as router_feedbacks
from app.endpoints.orders.router import router as router_orders
from app.endpoints.configs.router import router as router_configs
from app.endpoints.auth.router import router as router_auth
from app.endpoints.user.router import router as router_user

app = FastAPI()

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


@app.get("/")
def home_page():
    return {"message": "Сервер работает!"}


app.include_router(router_products)
app.include_router(router_categories)
app.include_router(router_feedbacks)
app.include_router(router_orders)
app.include_router(router_configs)

app.include_router(router_auth)
app.include_router(router_user)

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