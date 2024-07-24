"""Здесь находятся запросы к таблице курьеров в Бд"""

from app.database.models import async_session
from app.database.models import Courier
from sqlalchemy import select, update, delete


# Запрос на добавление курьера в БД
async def add_courier(name, surname, phone_number, tg_id):
    async with async_session() as session:
        session.add(Courier(name=name, surname=surname, rating=0, phone_number=phone_number, tg_id=tg_id))
        await session.commit()


# Запрос на изменение рейтинга курьера
async def change_rating(courier_id, rating_points):
    async with async_session() as session:
        await session.execute(update(Courier).where(Courier.id == courier_id).values(
            rating=Courier.rating+rating_points))
        await session.commit()


# Запрос на получение объекта курьера по telegram id
async def get_courier(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Courier).where(Courier.tg_id == tg_id))


# Запрос на вывод всех курьеров
async def get_all_couriers():
    async with async_session() as session:
        return await session.scalars(select(Courier))


# Запрос на получение объекта по id
async def get_courier_by_id(courier_id):
    async with async_session() as session:
        return await session.scalar(select(Courier).where(Courier.id == courier_id))


# Запрос на смену имени курьера
async def change_name(courier_id, new_name):
    async with async_session() as session:
        await session.execute(update(Courier).where(Courier.id == courier_id).values(name=new_name))
        await session.commit()


# Запрос на смену фамилии курьера
async def change_surname(courier_id, new_surname):
    async with async_session() as session:
        await session.execute(update(Courier).where(Courier.id == courier_id).values(surname=new_surname))
        await session.commit()


# Запрос на смену номера телефона курьера
async def change_number(courier_id, new_number):
    async with async_session() as session:
        await session.execute(update(Courier).where(Courier.id == courier_id).values(phone_number=new_number))
        await session.commit()


# Запрос на смену номера telegram id курьера
async def change_tg_id(courier_id, new_tg_id):
    async with async_session() as session:
        await session.execute(update(Courier).where(Courier.id == courier_id).values(tg_id=new_tg_id))
        await session.commit()


# Запрос на удаление курьера из БД
async def delete_courier(courier_id):
    async with async_session() as session:
        await session.execute(delete(Courier).where(Courier.id == courier_id))
        await session.commit()
