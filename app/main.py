from fastapi import FastAPI
from app.products.router import router as router_products

app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "Сервер работает!"}


app.include_router(router_products)