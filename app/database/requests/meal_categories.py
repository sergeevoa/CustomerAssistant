"""Здесь находятся запросы к таблице категорий блюд в Бд"""

from app.database.models import async_session
from app.database.models import MealCategory
from sqlalchemy import select, update, delete


# Запрос на добавление категории блюд в БД
async def add_meal_category(name, picture_link, restaurant_id):
    async with async_session() as session:
        session.add(MealCategory(name=name, picture_link=picture_link, restaurant_id=restaurant_id))
        await session.commit()


# Запрос на вывод всех категорий блюд из ресторана
async def get_meal_categories(restaurant_id):
    async with async_session() as session:
        return await session.scalars(select(MealCategory).where(MealCategory.restaurant_id == restaurant_id))


# Запрос на вывод категории блюда по id
async def get_meal_category(category_id):
    async with async_session() as session:
        return await session.scalar(select(MealCategory).where(MealCategory.id == category_id))


# Запрос на вывод первой категории блюда ресторана
async def get_first_category_from_restaurant(restaurant_id):
    async with async_session() as session:
        return await session.scalar(select(MealCategory).where(MealCategory.restaurant_id == restaurant_id))


# Запрос на обновление названия категории блюда
async def update_meal_category_name(category_id, new_name):
    async with async_session() as session:
        await session.execute(update(MealCategory).where(MealCategory.id == category_id).values(name=new_name))
        await session.commit()


# Запрос на обновление ссылки на фотографию категории блюда
async def update_meal_category_photo(category_id, new_picture_link):
    async with async_session() as session:
        await session.execute(update(MealCategory).where(MealCategory.id == category_id)
                              .values(picture_link=new_picture_link))
        await session.commit()


# Запрос на удаление категории блюда
async def delete_meal_category(category_id):
    async with async_session() as session:
        meal_category = await get_meal_category(category_id)
        restaurant_id = meal_category.restaurant_id
        await session.delete(meal_category)
        await session.commit()
        return restaurant_id
