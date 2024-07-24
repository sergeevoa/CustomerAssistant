"""Здесь находятся все запросы к таблице пользовательских запросов"""

from app.database.models import async_session
from app.database.models import Ticket
from sqlalchemy import select, delete

from app.database.requests.users import get_user


# Запрос на добавление сообщения о проблеме в БД
async def add_ticket(text, user_tg_id):
    async with async_session() as session:
        user = await get_user(user_tg_id)               # Получение объекта пользователя, отправившего сообщение
        session.add(Ticket(text=text, user_id=user.id))
        await session.commit()


# Запрос на вывод всех посланных пользовательских запросов
async def get_tickets():
    async with async_session() as session:
        return await session.scalars(select(Ticket))


# Запрос на вывод пользовательского запроса по id
async def get_ticket(ticket_id):
    async with async_session() as session:
        return await session.scalar(select(Ticket).where(Ticket.id == ticket_id))


# Запрос на удаление пользовательского запроса по id
async def delete_ticket(ticket_id):
    async with async_session() as session:
        await session.execute(delete(Ticket).where(Ticket.id == ticket_id))
        await session.commit()
