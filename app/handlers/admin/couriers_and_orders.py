"""Здесь будут храниться обработчики, связанные с просмотром информации о круьерах администратором"""

from aiogram import F, Router
from aiogram.types import Message
import app.database.requests.couriers as rq
import app.database.requests.orders as rq_ord
import app.filters as flt

courier_order_router = Router()
courier_order_router.message.filter(flt.CheckAdmin())
courier_order_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Вывести информацию о курьерах"
@courier_order_router.message(F.text == 'Вывести информацию о курьерах 🚴‍♂️🤖')
async def courier_check(message: Message):
    couriers = await rq.get_all_couriers()
    for courier in couriers:
        delivered_orders_number = len(list(await rq_ord.get_all_courier_completed_orders(courier.id)))
        await message.answer(f'Курьер № {courier.id}\nИмя: {courier.name} {courier.surname}\n'
                             f'Номер телефона: {courier.phone_number}\nКоличество доставок: {delivered_orders_number}\n'
                             f'Рейтинг: {courier.rating}')


# Обработчик нажатия на кнопку "Очистить таблицу заказов"
@courier_order_router.message(F.text == 'Очистить таблицу завершенных заказов 🧹')
async def delete_done_orders(message: Message):
    done_orders = await rq_ord.get_all_completed_orders()
    for order in done_orders:
        await rq_ord.delete_order_by_object(order)
    await message.answer('Информация о выполненных заказах успешно удалена.')
