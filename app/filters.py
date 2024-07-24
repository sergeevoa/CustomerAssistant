"""Здесь расположены фильтры, проверяющие права пользователя"""

from aiogram.filters import BaseFilter
from aiogram.types import Message

import app.database.requests.administrators as rq_adm
import app.database.requests.couriers as rq_cur
import app.database.requests.managers as rq_man


# Фильтр прав администратора для сообщений
class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message):     # Метод call позволяет обращаться к экземпляру класса как к функции
        try:
            # Запрос на получение объекта текущего пользователя с ролью администратора из таблицы администраторов
            return await rq_adm.get_admin(message.from_user.id)
        except:             # В случае любого бага возвращать false
            return False


# Фильтр прав курьера для сообщений
class CheckCourier(BaseFilter):
    async def __call__(self, message: Message):
        try:
            return await rq_cur.get_courier(message.from_user.id)
        except:
            return False


# Фильтр прав менеджера для сообщений
class CheckManager(BaseFilter):
    async def __call__(self, message: Message):
        try:
            return await rq_man.get_manager(message.from_user.id)
        except:
            return False
