"""Здесь находятся запросы к таблице администраторов в Бд"""

from app.database.models import async_session
from app.database.models import Admin
from sqlalchemy import select, update, delete


# Запрос на добавление администратора в БД
async def add_admin(name, surname, phone_number, tg_id):
    async with async_session() as session:
        session.add(Admin(name=name, surname=surname, is_active=True, phone_number=phone_number, tg_id=tg_id))
        await session.commit()


# Запрос на получение объекта администратора по telegram id
async def get_admin(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Admin).where(Admin.tg_id == tg_id))


# Запрос на вывод статуса администратора по tg_id
async def get_admin_status(admin_tg_id):
    async with async_session():
        admin = await get_admin(admin_tg_id)
        return admin.is_active


# Запрос на вывод всех администраторов
async def get_all_admins():
    async with async_session() as session:
        return await session.scalars(select(Admin))


# Запрос на получение объекта по id
async def get_admin_by_id(admin_id):
    async with async_session() as session:
        return await session.scalar(select(Admin).where(Admin.id == admin_id))


# Запрос на смену статуса активности администратора
async def change_status(admin_id, new_status):
    async with async_session() as session:
        await session.execute(update(Admin).where(Admin.id == admin_id).values(is_active=new_status))
        await session.commit()


# Запрос на смену имени администратора
async def change_name(admin_id, new_name):
    async with async_session() as session:
        await session.execute(update(Admin).where(Admin.id == admin_id).values(name=new_name))
        await session.commit()


# Запрос на смену фамилии администратора
async def change_surname(admin_id, new_surname):
    async with async_session() as session:
        await session.execute(update(Admin).where(Admin.id == admin_id).values(surname=new_surname))
        await session.commit()


# Запрос на смену номера телефона администратора
async def change_number(admin_id, new_number):
    async with async_session() as session:
        await session.execute(update(Admin).where(Admin.id == admin_id).values(phone_number=new_number))
        await session.commit()


# Запрос на смену номера telegram id администратора
async def change_tg_id(admin_id, new_tg_id):
    async with async_session() as session:
        await session.execute(update(Admin).where(Admin.id == admin_id).values(tg_id=new_tg_id))
        await session.commit()


# Запрос на удаление администратора из БД
async def delete_admin(admin_id):
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.id == admin_id))
        await session.commit()
