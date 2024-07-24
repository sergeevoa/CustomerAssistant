"""Здесь находятся запросы к таблице блюд в БД"""

from app.database.models import async_session
from app.database.models import Meal
from sqlalchemy import select, update


# Запрос на добавление блюда в БД
async def add_meal(name, compound, caloric_capacity, price, picture_link, category_id, restaurant_id):
    async with async_session() as session:
        session.add(Meal(name=name, compound=compound, caloric_capacity=caloric_capacity, price=price,
                         picture_link=picture_link, category_id=category_id, restaurant_id=restaurant_id))
        await session.commit()


# Запрос на вывод всех блюд из категории
async def get_meals(category_id):
    async with async_session() as session:
        return await session.scalars(select(Meal).where(Meal.category_id == category_id))


# Запрос на вывод блюда по id
async def get_meal(meal_id):
    async with async_session() as session:
        return await session.scalar(select(Meal).where(Meal.id == meal_id))


# Запрос на вывод первого блюда категории
async def get_first_meal_from_category(category_id):
    async with async_session() as session:
        return await session.scalar(select(Meal).where(Meal.category_id == category_id))


# Запрос на обновление названия блюда
async def update_meal_name(meal_id, new_name):
    async with async_session() as session:
        await session.execute(update(Meal).where(Meal.id == meal_id).values(name=new_name))
        await session.commit()


# Запрос на обновление состава блюда
async def update_meal_compound(meal_id, new_compound):
    async with async_session() as session:
        await session.execute(update(Meal).where(Meal.id == meal_id).values(compound=new_compound))
        await session.commit()


# Запрос на обновление значения калорийности блюда
async def update_meal_caloric_capacity(meal_id, new_caloric_capacity):
    async with async_session() as session:
        await session.execute(update(Meal).where(Meal.id == meal_id).values(caloric_capacity=new_caloric_capacity))
        await session.commit()


# Запрос на обновление цены блюда
async def update_meal_price(meal_id, new_price):
    async with async_session() as session:
        await session.execute(update(Meal).where(Meal.id == meal_id).values(price=new_price))
        await session.commit()


# Запрос на обновление фотографии блюда
async def update_meal_photo(meal_id, new_picture_link):
    async with async_session() as session:
        await session.execute(update(Meal).where(Meal.id == meal_id).values(picture_link=new_picture_link))
        await session.commit()


# Запрос на удаление блюда
async def delete_meal(meal_id):
    async with async_session() as session:
        meal = await get_meal(meal_id)
        meal_category_id = meal.category_id
        await session.delete(meal)
        await session.commit()
        return meal_category_id
