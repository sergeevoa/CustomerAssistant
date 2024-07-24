"""Здесь находятся обработчики, связанные с редактированием менеджеров"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.managers as kb
import app.keyboards.admin.database_editing.common_user_keyboards as kb_c
from app.keyboards.user.order_placing import all_restaurant_categories
import app.states as st
import app.database.requests.managers as rq
import app.filters as flt

from app.database.requests.restaurants import get_restaurant

manager_edit_router = Router()
manager_edit_router.message.filter(flt.CheckAdmin())
manager_edit_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Менеджеры"
@manager_edit_router.message(F.text == 'Менеджеры 👨‍💼️')
async def manager_edit_start(message: Message, state: FSMContext):
    await state.set_state(st.ManagerAddition.choose)
    await message.answer('Выберете категорию ресторана, в котором работают менеджеры:',
                         reply_markup=await all_restaurant_categories())


# Обработчик нажатия на кнопку ресторана в состоянии редактирования менеджеров
@manager_edit_router.callback_query(st.ManagerAddition.choose, F.data.startswith('restaurant_'))
async def manager_choosing(callback: CallbackQuery):
    await callback.answer('')
    restaurant = await get_restaurant(int(callback.data.split('_')[1]))
    await callback.message.edit_text(f'Список менеджеров ресторана {restaurant.name}:',
                                     reply_markup=await kb.managers(restaurant.id))


# Обработчик нажатия на кнопку "Добавить менеджера"
@manager_edit_router.callback_query(F.data.startswith('add_manager_'))
async def manager_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    restaurant_id = int(callback.data.split('_')[2])
    await state.set_state(st.ManagerAddition.restaurant_id)
    await state.update_data(restaurant_id=restaurant_id)
    await state.set_state(st.CommonUserAddition.role)
    await state.update_data(role=2)
    await state.set_state(st.CommonUserAddition.name)
    await callback.message.edit_text('Введите имя')


# Обработчик состояния нажатия на кнопку менеджера
@manager_edit_router.callback_query(F.data.startswith('manager_'))
async def manager_editing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.role)
    await state.update_data(role=2)
    manager = await rq.get_manager_by_id(int(callback.data.split('_')[1]))
    await callback.message.edit_text(f'Менеджер № {manager.id}:\n{manager.name} {manager.surname}\n'
                                     f'Номер телефона: {manager.phone_number}\nTelegram id: {manager.tg_id}',
                                     reply_markup=await kb_c.common_editing(manager.id, 2))


# Обработчик нажатия на кнопку "Назад" из меню просмотра менеджера
@manager_edit_router.callback_query(F.data == 'managers')
async def to_manager_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await manager_edit_start(callback.message, state)
