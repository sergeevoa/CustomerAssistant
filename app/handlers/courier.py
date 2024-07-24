"""Здесь расположены обработчики, связанные с главным меню курьера"""

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards.courier as kb
import app.database.requests.couriers as rq
import app.database.requests.users as rq_usr
import app.database.requests.orders as rq_ord
import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.meals as rq_m
import app.database.requests.order_collection_addresses as rq_ord_c
import app.database.requests.addresses as rq_addr
import app.filters as flt
import app.states as st

from app.keyboards.user.order_placing import deliver_approve

courier_router = Router()
courier_router.message.filter(flt.CheckCourier())
courier_router.callback_query.filter(flt.CheckCourier())


# Обработчик команды start для курьера в состоянии доставки заказа
@courier_router.message(Command('courier_start'), st.CourierOrderDeliver.delivering)
async def delivery_cmd_start(message: Message):
    await message.answer('Вы начали доставку заказа! Поторопитесь! 🚴‍♂️🔜', reply_markup=kb.delivering_end)


# Обработчик команды start для курьеров
@courier_router.message(Command('courier_start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    courier = await rq.get_courier(message.from_user.id)
    await message.answer(f'Приветствую, курьер {courier.name} {courier.surname} 🤝',
                         reply_markup=kb.courier_main_menu)


# Обработчик нажатия на кнопку "Вывести список заказов"
@courier_router.message(F.text == 'Вывести список заказов 🔍')
async def show_orders(message: Message):
    await message.answer('Доступные заказы 📝', reply_markup=await kb.all_cooking_orders())


# Обработчик нажатия на кнопку заказа
@courier_router.callback_query(F.data.startswith('get_order_'))
async def order_info(callback: CallbackQuery):
    await callback.answer('')
    order_id = int(callback.data.split('_')[2])
    order = await rq_ord.get_order(order_id)
    customer = await rq_usr.get_user_by_id(order.customer_id)

    deliver_address = await rq_addr.get_address(order.address_id)
    printable_deliver_address = (f'р-н {deliver_address.district}, ул. {deliver_address.street}, '
                                 f'д. {deliver_address.home}')
    if deliver_address.entrance and deliver_address.apartment:
        printable_deliver_address = printable_deliver_address + (f'п. {deliver_address.entrance}, '
                                                                 f'кв. {deliver_address.apartment}')

    ordered_meals = await rq_ord_m.get_all_ordered_meals(order_id)
    meals_names = ''
    for ordered_meal in ordered_meals:
        meal = await rq_m.get_meal(ordered_meal.meal_id)
        meals_names = meals_names + meal.name + ' x1\n'

    order_collection_addresses = await rq_ord_c.get_order_collection_addresses(order_id)
    printable_order_collection_addresses = ''
    for order_collection_address in order_collection_addresses:
        address = await rq_addr.get_address(order_collection_address.address_id)
        printable_order_collection_addresses = printable_order_collection_addresses + (f'{address.district} р-н, '
                                                                                       f'ул. {address.street}, '
                                                                                       f'д. {address.home}\n')

    await callback.message.answer(f'Заказ № {order_id}\n\nАдреса сбора заказа:\n{printable_order_collection_addresses}'
                                  f'\nАдрес доставки:\n{printable_deliver_address}\n\nСодержимое заказа\n{meals_names}'
                                  f'\nИмя клиента: {customer.username}\n Телефон: {customer.phone_number}',
                                  reply_markup=await kb.order_menu(order_id, customer.id))


# Обработчик нажатия на кнопку "Взять заказ"
@courier_router.callback_query(F.data.startswith('deliver_order_'))
async def order_delivery_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    order_id = int(callback.data.split('_')[2])
    customer_id = int(callback.data.split('_')[3])
    courier = await rq.get_courier(callback.from_user.id)
    await rq_ord.update_order_courier(order_id, courier.id)
    await state.set_state(st.CourierOrderDeliver.delivering)
    await state.update_data(order_id=order_id, customer_id=customer_id)
    await callback.message.answer('Вы начали доставку заказа! Поторопитесь! 🚴‍♂️🔜', reply_markup=kb.delivering_end)


# Обработчик нажатия на кнопку "Назад"
@courier_router.callback_query(F.data == 'cooked_order_list')
async def back_to_order_list(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь к доступным заказам')
    await show_orders(callback.message)


# Обработчик нажатия на кнопку "Завершить доставку"
@courier_router.message(F.text == 'Завершить доставку ✅', st.CourierOrderDeliver.delivering)
async def order_delivery_end(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    customer = await rq_usr.get_user_by_id(data["customer_id"])
    courier = await rq.get_courier(message.from_user.id)
    await bot.send_message(chat_id=customer.tg_id, text=f'Пожалуйста, подтвердите доставку вашего заказа номер '
                                                        f'{data["order_id"]}',
                           reply_markup=await deliver_approve(data["order_id"], courier.id))
    await message.answer('Ожидаю подтверждения от пользователя...⏳', reply_markup=kb.courier_main_menu)
    await state.clear()
