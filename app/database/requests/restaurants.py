"""Здесь находятся запросы к таблице ресторанов в Бд"""

from app.database.models import async_session
from app.database.models import Restaurant
from sqlalchemy import select, update


# Запрос на добавление ресторана в БД
async def add_restaurant(name, picture_link, category_id):
    async with async_session() as session:
        session.add(Restaurant(name=name, picture_link=picture_link, category_id=category_id))
        await session.commit()
        restaurant = await get_restaurant_by_name(name)
        return restaurant.id


# Запрос на вывод всех ресторанов из категории
async def get_category_restaurants(category_id):
    async with async_session() as session:
        return await session.scalars(select(Restaurant).where(Restaurant.category_id == category_id))


# Запрос на вывод ресторана по id
async def get_restaurant(restaurant_id):
    async with async_session() as session:
        return await session.scalar(select(Restaurant).where(Restaurant.id == restaurant_id))


# Запрос на вывод ресторана по названию
async def get_restaurant_by_name(restaurant_name):
    async with async_session() as session:
        return await session.scalar(select(Restaurant).where(Restaurant.name == restaurant_name))


# Запрос на вывод ресторана по id владельца
async def get_restaurant_by_owner(owner_id):
    async with async_session() as session:
        return await session.scalar(select(Restaurant).where(Restaurant.owner_id == owner_id))


# Запрос на вывод первого ресторана категории
async def get_first_restaurant_from_category(category_id):
    async with async_session() as session:
        return await session.scalar(select(Restaurant).where(Restaurant.category_id == category_id))


# Запрос на обновление названия ресторана
async def update_restaurant_name(restaurant_id, new_name):
    async with async_session() as session:
        await session.execute(update(Restaurant).where(Restaurant.id == restaurant_id).values(name=new_name))
        await session.commit()


# Запрос на обновление ссылки на фотографию ресторана
async def update_restaurant_photo(restaurant_id, new_picture_link):
    async with async_session() as session:
        await session.execute(update(Restaurant).where(Restaurant.id == restaurant_id)
                              .values(picture_link=new_picture_link))
        await session.commit()


# Запрос на обновление категории ресторана
async def update_restaurant_category(restaurant_id, new_category_id):
    async with async_session() as session:
        await session.execute(update(Restaurant).where(Restaurant.id == restaurant_id)
                              .values(category_id=new_category_id))
        await session.commit()


# Запрос на обновление id владельца ресторана
async def update_restaurant_owner(restaurant_id, owner_id):
    async with async_session() as session:
        await session.execute(update(Restaurant).where(Restaurant.id == restaurant_id)
                              .values(owner_id=owner_id))
        await session.commit()


# Запрос на удаление ресторана
async def delete_restaurant(restaurant_id):
    async with async_session() as session:
        restaurant = await get_restaurant(restaurant_id)
        rest_category_id = restaurant.category_id
        await session.delete(restaurant)
        await session.commit()
        return rest_category_id
