"""Здесь находятся запросы к таблице адресов сбора заказов в Бд"""

from app.database.models import async_session
from app.database.models import OrderCollectionAddress
from sqlalchemy import select, delete


# Запрос на добавление адреса сбора заказа
async def add_order_collection_address(order_id, address_id):
    async with async_session() as session:
        session.add(OrderCollectionAddress(order_id=order_id, address_id=address_id))
        await session.commit()


# Запрос на вывод всех адресов сбора заказа
async def get_order_collection_addresses(order_id):
    async with async_session() as session:
        return await session.scalars(select(OrderCollectionAddress).where(OrderCollectionAddress.order_id == order_id))


# Запрос на вывод адреса данного ресторана для сбора данного заказа
async def get_this_restaurant_order_collection_address(address_id, order_id):
    async with async_session() as session:
        return await session.scalar(select(OrderCollectionAddress).where(OrderCollectionAddress.order_id == order_id)
                                    .where(OrderCollectionAddress.address_id == address_id))


# Запрос на удаление всех адресов сбора заказа
async def delete_all_order_collection_addresses(order_id):
    async with async_session() as session:
        await session.execute(delete(OrderCollectionAddress).where(OrderCollectionAddress.order_id == order_id))
        await session.commit()
