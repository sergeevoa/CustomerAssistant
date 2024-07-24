"""Здесь находятся запросы к таблице пользователей в Бд"""

from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update


# Запрос на регистрацию нового пользователя
async def register_user(username, phone_number, tg_id):
    async with async_session() as session:  # Начинается сессия с БД
        session.add(User(  # Добавление пользователя в объект БД в программе
            username=username,
            phone_number=phone_number,
            tg_id=tg_id))
        await session.commit()  # Подтверждение изменений в самой БД


# Запрос на получение объекта пользователя по telegram id
async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


# Запрос на получение объекта пользователя по id
async def get_user_by_id(user_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == user_id))


# Запрос на обновление имени пользователя
async def update_username(tg_id, new_username):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(username=new_username))
        await session.commit()


# Запрос на обновление номера телефона
async def update_phone_number(tg_id, new_number):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(phone_number=new_number))
        await session.commit()


# Запрос на удаление пользователя
async def delete_user(user_tg_id):
    async with async_session() as session:
        user = await get_user(user_tg_id)
        await session.delete(user)
        await session.commit()
