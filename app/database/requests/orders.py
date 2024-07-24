"""Здесь находятся запросы к таблице заказов в Бд"""

from app.database.models import async_session
from app.database.models import Order
from sqlalchemy import select, update

from app.database.requests.users import get_user


# Запрос на создание объекта заказа
async def add_order(user_tg_id):
    async with async_session() as session:
        user = await get_user(user_tg_id)
        session.add(Order(status=0, price=0.0, customer_id=user.id, address_id=None))
        await session.commit()


# Запрос на вывод текущего заказа пользователя
async def get_current_order(user_tg_id):
    async with async_session() as session:
        user = await get_user(user_tg_id)
        return await session.scalar(select(Order).where(Order.customer_id == user.id).where(Order.status == 0))


# Запрос на вывод заказа по id
async def get_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id))


# Запрос на вывод завершенного заказа по id
async def get_completed_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id).where(Order.status == 4))


# Запрос на вывод доставляемого заказа по id
async def get_delivering_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id).where(Order.status == 3))


# Запрос на вывод всех актуальных заказов пользователя
async def get_all_customer_not_completed_orders(customer_id):
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.customer_id == customer_id).where(Order.status != 4).
                                     where(Order.status != 0))


# Запрос на вывод всех выполненных курьером заказов
async def get_all_courier_completed_orders(courier_id):
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.courier_id == courier_id).where(Order.status == 4))


# Запрос на проверку наличия у курьера незавершенных заказов
async def get_first_courier_not_completed_order(courier_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.courier_id == courier_id).where(Order.status != 4))


# Запрос на вывод всех размещенных заказов
async def get_all_placed_orders():
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.status == 1))


# Запрос на вывод всех готовящихся заказов
async def get_all_cooking_orders():
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.status == 2))


# Запрос на вывод всех завершенных заказов
async def get_all_completed_orders():
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.status == 4))


# Запрос на обновление цены заказа
async def update_order_price(order_id, price):
    async with async_session() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(price=Order.price + price))
        await session.commit()


# Запрос на обновление адреса доставки в заказе
async def update_order_address(user_tg_id, address_id):
    async with async_session() as session:
        user = await get_user(user_tg_id)
        await session.execute(update(Order).where(Order.customer_id == user.id).where(Order.status == 0).values(
            address_id=address_id))
        await session.commit()


# Запрос на запись id курьера в заказ и перевод его в статус "Доставляется"
async def update_order_courier(order_id, courier_id):
    async with async_session() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(courier_id=courier_id, status=3))
        await session.commit()


# Запрос на изменение статуса заказа
async def change_order_status(order_id, new_status):
    async with async_session() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(status=new_status))
        await session.commit()


# Запрос на удаление заказа из БД
async def delete_order(order_id):
    async with async_session() as session:
        order = await get_order(order_id)
        await session.delete(order)
        await session.commit()


# Запрос на удаление заказа из БД с передачей самого объекта заказа
async def delete_order_by_object(order):
    async with async_session() as session:
        await session.delete(order)
        await session.commit()
