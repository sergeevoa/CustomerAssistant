"""Здесь находятся обработчики, связанные с проверкой статуса заказа пользователем"""

from aiogram import F, Router
from aiogram.types import Message

import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.orders as rq_ord
import app.database.requests.users as rq_usr
import app.database.requests.meals as rq_m

order_checkout_router = Router()


# Обработчик состояния нажатия на кнопку "Мои заказы"
@order_checkout_router.message(F.text == 'Мои заказы 📝')
async def show_orders(message: Message):
    customer = await rq_usr.get_user(message.from_user.id)
    orders = await rq_ord.get_all_customer_not_completed_orders(customer.id)

    printable_status = 'Не оформлен'
    for order in orders:
        if order.status == 1:
            printable_status = 'Оформлен'
        elif order.status == 2:
            printable_status = 'Готовится'
        elif order.status == 3:
            printable_status = 'Доставляется'

        ordered_meals = await rq_ord_m.get_all_ordered_meals(order.id)
        meal_names = ''
        for ordered_meal in ordered_meals:
            meal = await rq_m.get_meal(ordered_meal.meal_id)
            meal_names = meal_names + '\n' + meal.name

        await message.answer(f'Заказ № {order.id}\n\n'
                             f'Статус: {printable_status}\n\n'
                             f'Содержит:{meal_names}\n\n'
                             f'Стоимость: {round(order.price, 2)}')
