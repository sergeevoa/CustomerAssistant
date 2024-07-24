"""Здесь находятся обработчики, связанные с редактированием курьеров"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.couriers as kb
import app.keyboards.admin.database_editing.common_user_keyboards as kb_c
import app.states as st
import app.database.requests.couriers as rq
import app.filters as flt

courier_edit_router = Router()
courier_edit_router.message.filter(flt.CheckAdmin())
courier_edit_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Курьеры"
@courier_edit_router.message(F.text == 'Курьеры 🚴‍♂️')
async def courier_edit_start(message: Message):
    await message.answer(f'Список курьеров 🚴‍♂️:', reply_markup=await kb.couriers())


# Обработчик нажатия на кнопку "Добавить курьера"
@courier_edit_router.callback_query(F.data.startswith('add_courier'))
async def courier_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserAddition.role)
    await state.update_data(role=1)
    await state.set_state(st.CommonUserAddition.name)
    await callback.message.edit_text('Введите имя')


# Обработчик состояния нажатия на кнопку курьера
@courier_edit_router.callback_query(F.data.startswith('courier_'))
async def admin_editing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.role)
    await state.update_data(role=1)
    courier = await rq.get_courier_by_id(int(callback.data.split('_')[1]))
    await callback.message.edit_text(f'Курьер № {courier.id}:\n{courier.name} {courier.surname}\n'
                                     f'Рейтинг: {courier.rating}\nНомер телефона: {courier.phone_number}\n'
                                     f'Telegram id: {courier.tg_id}',
                                     reply_markup=await kb_c.common_editing(courier.id, 1))


# Обработчик нажатия на кнопку "Назад" из меню просмотра курьера
@courier_edit_router.callback_query(F.data == 'couriers')
async def to_courier_list(callback: CallbackQuery):
    await callback.answer('')
    await courier_edit_start(callback.message)
