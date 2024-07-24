"""Здесь хранится структура базы данных"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, ForeignKey

import os
from dotenv import load_dotenv

load_dotenv()

# Создание объекта БД
# echo позволяет выводить действие в БД в терминал
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'), echo=True)

# Создание асинхронного класса sessionmaker для подключения к БД
async_session = async_sessionmaker(engine)


# Основной класс БД, позволяющий управлять дочерними классами (таблицами БД)
class Base(AsyncAttrs, DeclarativeBase):

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):  # Метод для красивого вывода SQLAlchemy запросов и их результатов в консоль
        """Relationship не используется в repr, так как может вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


# Класс, отражающий модель сущности клиента
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(16), nullable=False)
    tg_id = mapped_column(BigInteger, nullable=False)

    # Отношение к адресам: один ко многим
    addresses = relationship(
        # Этот параметр содержит название класса, с которым выстраивается отношение
        argument='Address',
        # Параметр содержит название relationship-а связанного класса, который отвечает за связь с данным классом
        back_populates='user_addresses',
        # Аргумент для каскадного удаления всех объектов класса Address,
        # связанных с удаляемым объектом класса User
        cascade='save-update, merge, delete'
    )

    # Отношение к запросам: один ко многим
    tickets = relationship(
        argument='Ticket',
        back_populates='user',
        cascade='save-update, merge, delete'
    )

    # Отношение к заказам: один ко многим
    orders = relationship(
        argument='Order',
        back_populates='user',
        # Параметр необходим при наличии в связываемом классе нескольких внешних ключей на объекты данного класса
        # foreign_keys=Order.customer_id,
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности администратора
class Admin(Base):
    __tablename__ = 'administrators'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=False)
    # Этот параметр показывает, как использует бота в данный момент администратор:
    # как администратор или как пользователь.
    is_active: Mapped[bool] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(String(16), nullable=False)
    tg_id = mapped_column(BigInteger, nullable=False)


# Класс, отражающий модель сущности курьера
class Courier(Base):
    __tablename__ = 'couriers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=False)
    # Параметр отображает качество работы курьера. Чем выше значение - тем лучше курьер работал.
    rating: Mapped[int] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(String(16), nullable=False)
    tg_id = mapped_column(BigInteger, nullable=False)

    # Отношение к заказам: один ко многим
    orders = relationship(
        argument='Order',
        back_populates='courier',
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности менеджера ресторана
class Manager(Base):
    __tablename__ = 'managers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(16), nullable=False)
    tg_id = mapped_column(BigInteger, nullable=False)
    restaurant_id = mapped_column(ForeignKey('restaurants.id'), nullable=False)

    # Отношение к ресторанам: многие к одному
    restaurant = relationship(
        argument='Restaurant',
        back_populates='managers'
    )


# Класс, отражающий модель сущности пользовательского запроса
class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1024), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    # Отношение к пользователям: многие к одному
    user = relationship(
        argument='User',
        back_populates='tickets'
    )


# Класс, отражающий модель сущности адреса
class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    district: Mapped[str] = mapped_column(String(20), nullable=False)
    street: Mapped[str] = mapped_column(String(20), nullable=False)
    home: Mapped[str] = mapped_column(String(20), nullable=False)
    entrance: Mapped[int] = mapped_column(nullable=True)
    apartment: Mapped[int] = mapped_column(nullable=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.id'), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)

    # Связь с ресторанами: многие к одному
    restaurant_addresses = relationship(
        argument='Restaurant',
        back_populates='addresses'
    )

    # Связь с пользователями: многие к одному
    user_addresses = relationship(
        argument='User',
        back_populates='addresses'
    )

    # Связь с адресами сбора заказа: один ко многим
    order_collection_addresses = relationship(
        argument='OrderCollectionAddress',
        back_populates='address',
        cascade='save-update, merge, delete'
    )

    # Отношение к заказам: один ко многим
    orders = relationship(
        argument='Order',
        back_populates='address',
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности категории ресторана
class RestaurantCategory(Base):
    __tablename__ = 'restaurant_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String[40], nullable=False)

    # Отношение к ресторанам: один ко многим
    restaurants = relationship(
        argument='Restaurant',
        back_populates='restaurant_category',
        cascade='save-update, merge, delete',
    )


# Класс, отражающий модель сущности ресторана
class Restaurant(Base):
    __tablename__ = 'restaurants'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String[40], nullable=False)
    picture_link: Mapped[str] = mapped_column(String[83], nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('restaurant_categories.id'), nullable=False)

    # Отношение к категории ресторанов: многие к одному
    restaurant_category = relationship(
        argument='RestaurantCategory',
        back_populates='restaurants'
    )

    # Отношение к категориям блюд: один ко многим
    meal_categories = relationship(
        argument='MealCategory',
        back_populates='restaurant',
        cascade='save-update, merge, delete'
    )

    # Отношение к адресам: один ко многим
    addresses = relationship(
        argument='Address',
        back_populates='restaurant_addresses',
        cascade='save-update, merge, delete'
    )

    # Отношение к менеджерам: один ко многим
    managers = relationship(
        argument='Manager',
        back_populates='restaurant',
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности категории блюд
class MealCategory(Base):
    __tablename__ = 'meal_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String[30], nullable=False)
    picture_link: Mapped[str] = mapped_column(String[83], nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.id'), nullable=False)

    # Отношение к ресторанам: многие к одному
    restaurant = relationship(
        argument='Restaurant',
        back_populates='meal_categories'
    )

    # Отношение к блюдам: один ко многим
    meals = relationship(
        argument='Meal',
        back_populates='meal_category',
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности блюда
class Meal(Base):
    __tablename__ = 'meals'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String[30], nullable=False)
    compound: Mapped[str] = mapped_column(String[50], nullable=False)
    caloric_capacity: Mapped[int] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    picture_link: Mapped[str] = mapped_column(String[83], nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('meal_categories.id'), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.id'), nullable=False)

    # Отношение к категориям блюд. Многие к одному
    meal_category = relationship(
        argument='MealCategory',
        back_populates='meals'
    )

    # Отношение к заказанным блюдам. Один ко многим
    ordered_meals = relationship(
        argument='OrderedMeal',
        back_populates='meal',
        cascade='save-update, merge, delete'
    )


# Класс, отражающий модель сущности заказа
class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    # 0 - заказ создан. 1 - заказ размещен, 2 - заказ готовится, 3 - заказ доставляется, 4 - заказ выполнен
    status: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    courier_id: Mapped[int] = mapped_column(ForeignKey('couriers.id'), nullable=True)
    address_id: Mapped[int] = mapped_column(ForeignKey('addresses.id'), nullable=True)

    # Отношение к пользователям: многие к одному
    user = relationship(
        argument='User',
        back_populates='orders'
    )

    # Отношение к адресу доставки: многие к одному
    address = relationship(
        argument='Address',
        back_populates='orders'
    )

    # Отношение к заказанным блюдам: один ко многим
    ordered_meals = relationship(
        argument='OrderedMeal',
        back_populates='order',
        cascade='save-update, merge, delete'
    )

    # Отношение к адресам сбора заказа: один ко многим
    order_collection_addresses = relationship(
        argument='OrderCollectionAddress',
        back_populates='order',
        cascade='save-update, merge, delete'
    )

    # Отношение к курьерам: многие к одному
    courier = relationship(
        argument='Courier',
        back_populates='orders'
    )


# Класс отражающий модель сущности заказанного блюда
class OrderedMeal(Base):
    __tablename__ = 'ordered_meals'

    id: Mapped[int] = mapped_column(primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey('meals.id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)

    # Отношение к заказам: многие к одному
    order = relationship(
        argument='Order',
        back_populates='ordered_meals'
    )

    # Отношение к блюдам: многие к одному
    meal = relationship(
        argument='Meal',
        back_populates='ordered_meals'
    )


# Класс, отражающий модель сущности адреса сбора заказа
class OrderCollectionAddress(Base):
    __tablename__ = 'order_collection_addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey('addresses.id'), nullable=False)

    # Отношение к заказу: многие к одному
    order = relationship(
        argument='Order',
        back_populates='order_collection_addresses'
    )

    # Отношение к адресу: многие к одному
    address = relationship(
        argument='Address',
        back_populates='order_collection_addresses'
    )


async def async_main():
    async with engine.begin() as conn:  # Начало сессии с БД и обозначение ее как conn
        await conn.run_sync(Base.metadata.create_all)
