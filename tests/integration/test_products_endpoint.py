import pytest
from app.database import async_session_maker
from app.models import Feedback, Vendor


# ==================== GET /products/ Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_all_products(product_factory, async_client):
    """Получение списка активных товаров без фильтров."""
    p1 = await product_factory(name="Товар 1", price=100.0)
    p2 = await product_factory(name="Товар 2", price=200.0)

    response = await async_client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    returned_ids = {p["id"] for p in data}
    assert p1.id in returned_ids
    assert p2.id in returned_ids


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_disabled_excluded(product_factory, async_client):
    """Товары с enabled=False не возвращаются в общем списке."""
    active_prod = await product_factory(name="Активный товар", enabled=True)
    await product_factory(name="Отключенный товар", enabled=False)

    response = await async_client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == active_prod.id


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_filter_by_category(category_factory, product_factory, async_client):
    """Фильтрация товаров по category_id."""
    cat1 = await category_factory(name="Категория 1")
    cat2 = await category_factory(name="Категория 2")

    p1 = await product_factory(category_id=cat1.id, name="Товар из категории 1")
    await product_factory(category_id=cat2.id, name="Товар из категории 2")

    response = await async_client.get(f"/products/?category_id={cat1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == p1.id
    assert data[0]["category_id"] == cat1.id


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_filter_by_name(product_factory, async_client):
    """Поиск товаров по подстроке названия без учета регистра (ilike)."""
    p1 = await product_factory(name="Красное ЯБЛОКО")
    p2 = await product_factory(name="Зеленое яблоко")
    await product_factory(name="Сладкий банан")

    response = await async_client.get("/products/?name=яблоко")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    returned_ids = {p["id"] for p in data}
    assert p1.id in returned_ids
    assert p2.id in returned_ids


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_filter_by_similar(product_factory, async_client):
    """Фильтр similar ищет товары с одинаковыми первыми 4 символами ID, исключая сам товар."""
    main_prod = await product_factory(product_id="appl0001", name="Яблоко Голден")
    similar_prod = await product_factory(product_id="appl0002", name="Яблоко Фуджи")
    await product_factory(product_id="oran0001", name="Апельсин")

    response = await async_client.get(f"/products/?similar={main_prod.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == similar_prod.id


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_sorting_price_asc(product_factory, async_client):
    """Сортировка товаров по возрастанию цены (price_asc)."""
    await product_factory(name="Дорогой", price=300.0)
    await product_factory(name="Дешевый", price=50.0)
    await product_factory(name="Средний", price=150.0)

    response = await async_client.get("/products/?sorting=price_asc")
    assert response.status_code == 200
    prices = [p["price"] for p in response.json()]
    assert prices == [50.0, 150.0, 300.0]


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_sorting_price_desc(product_factory, async_client):
    """Сортировка товаров по убыванию цены (price_desc)."""
    await product_factory(name="Дорогой", price=300.0)
    await product_factory(name="Дешевый", price=50.0)
    await product_factory(name="Средний", price=150.0)

    response = await async_client.get("/products/?sorting=price_desc")
    assert response.status_code == 200
    prices = [p["price"] for p in response.json()]
    assert prices == [300.0, 150.0, 50.0]


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_sorting_popularity(product_factory, async_client):
    """Сортировка товаров по популярности (количеству заказов order_count desc)."""
    await product_factory(name="Мало заказов", order_count=2)
    await product_factory(name="Хит продаж", order_count=50)
    await product_factory(name="Средне заказов", order_count=15)

    response = await async_client.get("/products/?sorting=popularity")
    assert response.status_code == 200
    counts = [p["order_count"] for p in response.json()]
    assert counts == [50, 15, 2]


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_sorting_new(product_factory, async_client):
    """Сортировка товаров со статусом new в начало списка."""
    await product_factory(name="Обычный товар", status="default")
    new_prod = await product_factory(name="Новинка", status="new")

    response = await async_client.get("/products/?sorting=new")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["id"] == new_prod.id
    assert data[0]["status"] == "new"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_sorting_sale(product_factory, async_client):
    """Сортировка товаров со статусом sale в начало списка."""
    await product_factory(name="Обычный товар", status="default")
    sale_prod = await product_factory(name="Акционный товар", status="sale")

    response = await async_client.get("/products/?sorting=sale")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["id"] == sale_prod.id
    assert data[0]["status"] == "sale"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_products_not_found(async_client):
    """Возврат 404, если товары по заданному фильтру не найдены."""
    response = await async_client.get("/products/?name=несуществующий_товар_12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ==================== GET /products/{id} Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_product_by_id_full_details(product_factory, db_category, async_client):
    """Получение детальной информации о товаре с поставщиками, отзывами и похожими товарами."""
    prod = await product_factory(
        product_id="item0001",
        name="Премиум товар",
        description="Подробное описание товара",
        rating=4.9
    )
    # Похожий товар (первые 4 символа item совпадают)
    similar_prod = await product_factory(
        product_id="item0002",
        name="Похожий товар"
    )

    # Добавляем поставщика и отзывы в БД
    async with async_session_maker() as session:
        async with session.begin():
            vendor = Vendor(name="ООО Агропоставка")
            session.add(vendor)
            await session.flush()

            # Привязываем поставщика к товару через промежуточную таблицу
            from app.models import product_vendors
            await session.execute(
                product_vendors.insert().values(product_id=prod.id, vendor_id=vendor.id)
            )

            # Добавляем отзыв к товару
            feedback = Feedback(
                product_id=prod.id,
                rating=5,
                comment="Отличный товар, рекомендую!"
            )
            session.add(feedback)
            await session.flush()
            await session.commit()

    response = await async_client.get(f"/products/{prod.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == prod.id
    assert data["name"] == "Премиум товар"
    assert data["description"] == "Подробное описание товара"
    assert data["rating"] == 4.9
    assert data["vendors"] == ["ООО Агропоставка"]
    assert len(data["feedbacks"]) == 1
    assert data["feedbacks"][0]["rating"] == 5
    assert data["feedbacks"][0]["comment"] == "Отличный товар, рекомендую!"
    assert len(data["similars"]) == 1
    assert data["similars"][0]["id"] == similar_prod.id


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_product_by_id_limits(product_factory, async_client):
    """Проверка ограничения выдачи отзывов (max 3) и похожих товаров (max 3)."""
    main_prod = await product_factory(product_id="limt0001", name="Основной товар")

    # Создаем 5 похожих товаров
    for i in range(2, 7):
        await product_factory(product_id=f"limt{i:04d}", name=f"Похожий {i}")

    # Создаем 5 отзывов
    async with async_session_maker() as session:
        async with session.begin():
            for i in range(5):
                session.add(Feedback(
                    product_id=main_prod.id,
                    rating=5,
                    comment=f"Отзыв {i}"
                ))
            await session.commit()

    response = await async_client.get(f"/products/{main_prod.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["feedbacks"]) == 3
    assert len(data["similars"]) == 3


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_product_by_id_not_found(async_client):
    """Возврат 404 для несуществующего идентификатора товара."""
    response = await async_client.get("/products/nonexist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product with id 'nonexist' not found"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_product_by_id_disabled_returns_404(product_factory, async_client):
    """Возврат 404 для товара с enabled=False."""
    disabled_prod = await product_factory(name="Скрытый товар", enabled=False)

    response = await async_client.get(f"/products/{disabled_prod.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Product with id '{disabled_prod.id}' not found"
