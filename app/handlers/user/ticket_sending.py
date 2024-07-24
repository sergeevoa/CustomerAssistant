"""Здесь находятся обработчики команд, callback-ов и состояний, связанных с отправкой запроса в техноддержку"""

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.database.requests.tickets as rq_tick
import app.database.requests.orders as rq_ord
import app.database.requests.couriers as rq_cur
import app.keyboards.user.ticket_sending as kb
import app.keyboards.user.main_menu as kb_m
import app.states as st


ticket_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение


# Обработчик кнопки главного меню "Сообщить о проблеме"
@ticket_router.message(F.text == 'Сообщить о проблеме ⚠️')
async def problems_menu(message: Message):
    await message.answer('Если у вас возникла одна из этих проблем, кликните по соответствующей кнопке и я помогу вам '
                         '🦉\nЕсли у вас другая проблема, кликните на последнюю кнопку и отправьте запрос в нашу '
                         'техподдежку', reply_markup=kb.common_problems)


# Обработчик нажатия на кнопку "Доставили не мой заказ"
@ticket_router.callback_query(F.data == 'wrong_order')
async def wrong_order_id_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.WrongOrder.order_id)
    await callback.message.answer('Приношу глубочайшие извинения за такую ситуацию!\n'
                                  'Я отправлю послание своим администраторам, '
                                  'они разберутся в ситуации и обязательно вернут вам деньги.\n'
                                  'Пожалуйста, укажите номер вашего заказа:')


# Обработчик состояния ввода id перепутанного заказа
@ticket_router.message(st.WrongOrder.order_id, lambda message: message.text.isdigit())
async def wrong_order_id_getting(message: Message, state: FSMContext):
    order_id = int(message.text)
    if await rq_ord.get_completed_order(order_id):
        await state.update_data(order_id=order_id)
        await state.set_state(st.WrongOrder.order_photo)
        await message.answer('Теперь отправьте фото содержимого заказа, который вам пришел:')
    else:
        await message.answer('Такого заказа нет среди доставленных!', reply_markup=kb_m.main_menu)
        await state.clear()


# Обработчик состояния отправки фотографии перепутанного заказа
@ticket_router.message(st.WrongOrder.order_photo, F.photo)
async def wrong_order_photo_getting(message: Message, state: FSMContext):
    data = await state.get_data()
    picture_link = message.photo[-1].file_id
    text = (f'Жалоба на перепутанный заказ. Просьба сравнить фото с заказом пользователя и вернуть '
            f'пользователю деньги в случае правдивости его слов.\nНомер заказа: {data["order_id"]}\nСсылка на фото:\n'
            f'{picture_link}')
    await rq_tick.add_ticket(text, message.from_user.id)
    await message.answer('Ваша жалоба передана администраторам! Если все верно, ждите возврата средств в течение дня ⏳')


# Обработчик состояния нажатия на кнопку "Курьер заблудился"
@ticket_router.callback_query(F.data == 'lost_courier')
async def lost_courier_incident_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.LostCourier.order_id)
    await callback.message.answer('Введите id заказа и я дам вам контакты курьера:')


# Обработчик состояния ввода id при инциденте с потерянным курьером
@ticket_router.message(st.LostCourier.order_id, lambda message: message.text.isdigit())
async def wrong_order_id_getting(message: Message, state: FSMContext):
    order_id = int(message.text)
    order = await rq_ord.get_delivering_order(order_id)
    if order:
        courier = await rq_cur.get_courier_by_id(order.courier_id)
        await message.answer(f'Имя курьера: {courier.surname} {courier.name}\n'
                             f'Телефон курьера: {courier.phone_number}\n'
                             f'При необходимости можете написать курьеру прямо здесь:',
                             reply_markup=await kb.text_to_courier(courier.id))
    else:
        await message.answer('Такого заказа нет среди доставляемых в данный момент!', reply_markup=kb_m.main_menu)
    await state.clear()


# Обработчик нажатия на кнопку "Написать курьеру"
@ticket_router.callback_query(F.data.startswith('text_courier_'))
async def text_courier_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Напишите ваше сообщение', show_alert=True)
    await state.set_state(st.LostCourier.text_courier)
    await state.update_data(courier_id=int(callback.data.split('_')[2]))


# Обработчик состояния сообщения заблудившемуся курьеру
@ticket_router.message(st.LostCourier.text_courier)
async def text_courier_end(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    courier = await rq_cur.get_courier_by_id(data["courier_id"])
    await bot.send_message(chat_id=courier.tg_id, text=message.text)
    await message.answer('Сообщение курьеру отправлено!', reply_markup=kb_m.main_menu)


# Обработчик нажатия на кнопку "Некорректное поведение курьера"
@ticket_router.callback_query(F.data.startswith('angry_courier'))
async def angry_courier_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Укажите номер заказа, при доставке которого вам нахамил курьер', show_alert=True)
    await state.set_state(st.AngryCourier.order_id)


# Обработчик состояния ввода id нерадивого курьера
@ticket_router.message(st.AngryCourier.order_id, lambda message: message.text.isdigit())
async def angry_courier_punishment(message: Message, state: FSMContext):
    order_id = int(message.text)
    order = await rq_ord.get_completed_order(order_id)
    if order:
        angry_courier = await rq_cur.get_courier_by_id(order.courier_id)
        await rq_cur.change_rating(angry_courier.id, -10)
        await message.answer('Рейтинг курьера, доставлявшего ваш заказ, снижен, '
                             'что напрямую скажется на его зарплате! 🥳', reply_markup=kb_m.main_menu)
    else:
        await message.answer('Такого заказа нет среди доставленных!')
    await state.clear()


# Обработчик кнопки "Другая проблема"
@ticket_router.callback_query(F.data == 'new_ticket')
async def ticket_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Пожалуйста, опишите вашу проблему как можно подробнее', show_alert=True)
    await state.set_state(st.TicketWriting.text)


# Обработчик состояния ввода текста сообщения о проблеме
@ticket_router.message(st.TicketWriting.text)
async def ticket_writing(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    await rq_tick.add_ticket(data["text"], message.from_user.id)
    await message.answer('Ваш запрос успешно отправлен! Ждите ответа... ⏳', reply_markup=kb_m.main_menu)
    await state.clear()
