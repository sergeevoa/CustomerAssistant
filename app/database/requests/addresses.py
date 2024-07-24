"""Здесь находятся запросы к таблице адресов в Бд"""

from app.database.models import async_session
from app.database.models import Address
from sqlalchemy import select


# Запрос на добавление объекта адреса
async def set_address(district, street, home, entrance, apartment, restaurant_id, owner_id):
    async with async_session() as session:
        session.add(Address(district=district, street=street, home=home, entrance=entrance, apartment=apartment,
                            restaurant_id=restaurant_id, owner_id=owner_id))
        await session.commit()


# Запрос на вывод адреса по id
async def get_address(address_id):
    async with async_session() as session:
        return await session.scalar(select(Address).where(Address.id == address_id))


# Запрос на вывод всех адресов пользователя
async def get_user_addresses(user_id):
    async with async_session() as session:
        return await session.scalars(select(Address).where(Address.owner_id == user_id))


# Запрос на вывод всех адресов ресторана
async def get_restaurant_addresses(restaurant_id):
    async with async_session() as session:
        return await session.scalars(select(Address).where(Address.restaurant_id == restaurant_id))
