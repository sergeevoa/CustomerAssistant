"""Здесь находятся запросы к таблице менеджеров в Бд"""

from app.database.models import async_session
from app.database.models import Manager
from sqlalchemy import select, update, delete


# Запрос на добавление в БД
async def add_manager(name, surname, phone_number, tg_id, restaurant_id):
    async with async_session() as session:
        session.add(Manager(name=name, surname=surname, phone_number=phone_number, tg_id=tg_id,
                            restaurant_id=restaurant_id))
        await session.commit()


# Запрос на получение объекта по telegram id
async def get_manager(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Manager).where(Manager.tg_id == tg_id))


# Запрос на вывод всех менеджеров из данного ресторана
async def get_all_managers_from_restaurant(restaurant_id):
    async with async_session() as session:
        return await session.scalars(select(Manager).where(Manager.restaurant_id == restaurant_id))


# Запрос на получение объекта по id
async def get_manager_by_id(manager_id):
    async with async_session() as session:
        return await session.scalar(select(Manager).where(Manager.id == manager_id))


# Запрос на смену имени
async def change_name(manager_id, new_name):
    async with async_session() as session:
        await session.execute(update(Manager).where(Manager.id == manager_id).values(name=new_name))
        await session.commit()


# Запрос на смену фамилии
async def change_surname(manager_id, new_surname):
    async with async_session() as session:
        await session.execute(update(Manager).where(Manager.id == manager_id).values(surname=new_surname))
        await session.commit()


# Запрос на смену номера телефона
async def change_number(manager_id, new_number):
    async with async_session() as session:
        await session.execute(update(Manager).where(Manager.id == manager_id).values(phone_number=new_number))
        await session.commit()


# Запрос на смену telegram id
async def change_tg_id(manager_id, new_tg_id):
    async with async_session() as session:
        await session.execute(update(Manager).where(Manager.id == manager_id).values(tg_id=new_tg_id))
        await session.commit()


# Запрос на удаление менеджера из БД
async def delete_manager(manager_id):
    async with async_session() as session:
        await session.execute(delete(Manager).where(Manager.id == manager_id))
        await session.commit()
