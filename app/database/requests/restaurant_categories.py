"""Здесь находятся запросы к таблице категорий ресторанов в Бд"""

from app.database.models import async_session
from app.database.models import RestaurantCategory
from sqlalchemy import select, update


# Запрос на создание категории ресторанов
async def add_restaurant_category(name):
    async with async_session() as session:
        session.add(RestaurantCategory(name=name))
        await session.commit()


# Запрос на вывод категории ресторана по id
async def get_restaurant_category(category_id):
    async with async_session() as session:
        return await session.scalar(select(RestaurantCategory).where(RestaurantCategory.id == category_id))


# Запрос на вывод всех категорий ресторанов
async def get_restaurant_categories():
    async with async_session() as session:
        return await session.scalars(select(RestaurantCategory))


# Запрос на вывод всех категорий ресторанов кроме указанной
async def get_all_categories_except_this(category_id):
    async with async_session() as session:
        return await session.scalars(select(RestaurantCategory).where(RestaurantCategory.id != category_id))


# Запрос на обновление названия категории
async def update_name(category_id, new_name):
    async with async_session() as session:
        await session.execute(update(RestaurantCategory).where(RestaurantCategory.id == category_id).values(
            name=new_name))
        await session.commit()


# Запрос на удаление категории
async def delete_category(category_id):
    async with async_session() as session:
        # При удалении категории происходит каскадное удаление всех ресторанов, входящих в категорию.
        # При этом операция session.execute(delete...) не поддерживает каскадное удаление, так как только имитирует
        # DELETE заголовок и не видит зависимые от удаляемого объекты
        # Поэтому необходимо сначала найти удаляемый объект через session.scalar(),
        # а потом удалить его поместив в session.delete
        category = await get_restaurant_category(category_id)
        await session.delete(category)
        await session.commit()
