"""Здесь находятся запросы к таблице заказанных блюд в Бд"""

from app.database.models import async_session
from app.database.models import OrderedMeal
from sqlalchemy import select, delete

import app.database.requests.orders as rq_ord


# Запрос на добавление заказанного блюда
async def add_ordered_meal(meal_id, order_id):
    async with async_session() as session:
        session.add(OrderedMeal(meal_id=meal_id, order_id=order_id))
        await session.commit()


# Запрос на вывод всех блюд заказа
async def get_all_ordered_meals(order_id):
    async with async_session() as session:
        return await session.scalars(select(OrderedMeal).where(OrderedMeal.order_id == order_id))


# Запрос на вывод одного блюда заказа
async def get_ordered_meal(order_id, meal_id):
    async with async_session() as session:
        return await session.scalar(select(OrderedMeal).where(OrderedMeal.order_id == order_id).where(
            OrderedMeal.meal_id == meal_id))


# Запрос на вывод первого блюда определенного типа из любого заказа
async def get_first_ordered_meal(meal_id):
    async with async_session() as session:
        return await session.scalar(select(OrderedMeal).where(OrderedMeal.meal_id == meal_id))


# Запрос на вывод всех записей с данным заказанным блюдом
async def get_all_records_with_this_meal(meal_id):
    async with async_session() as session:
        return await session.scalars(select(OrderedMeal).where(OrderedMeal.meal_id == meal_id))


# Запрос на поиск незавершенных заказов, в которых имеется данное блюдо
async def is_this_meal_in_active_orders(meal_id):
    records = await get_all_records_with_this_meal(meal_id)
    for record in records:
        order = await rq_ord.get_order(record.order_id)
        if order.status != 4:
            return True
    return False


# Запрос на удаление заказанного блюда
async def delete_ordered_meal(order_id, meal_id):
    async with async_session() as session:
        meal = await get_ordered_meal(order_id, meal_id)
        await session.execute(delete(OrderedMeal).where(OrderedMeal.id == meal.id))
        await session.commit()


# Запрос на удаление всех блюд из одного заказа
async def delete_all_ordered_meals(order_id):
    async with async_session() as session:
        await session.execute(delete(OrderedMeal).where(OrderedMeal.order_id == order_id))
        await session.commit()
