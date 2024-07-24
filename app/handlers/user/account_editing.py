"""Здесь находятся обработчики, связанные с оформлением заказа пользователем"""

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.user.account_editing as kb
import app.keyboards.user.main_menu as kb_menu
import app.states as st
import app.database.requests.users as rq


user_data_edit_router = Router()


# Обработчик нажатия на кнопку "Редактировать профиль"
@user_data_edit_router.message(F.text == 'Редактировать профиль ⚙️')
async def account_edit_start(message: Message):
    await message.answer('Что именно вы хотите редактировать? 🤔', reply_markup=kb.data_choosing)


# Обработчик нажатия на кнопку "Изменить имя"
@user_data_edit_router.message(F.text == 'Изменить имя 🗣')
async def name_changing(message: Message, state: FSMContext):
    await state.set_state(st.UserEditing.name)
    await message.answer('Введите новое имя')


# Обработчик состояния изменения имени
@user_data_edit_router.message(st.UserEditing.name)
async def name_update(message: Message, state: FSMContext):
    await rq.update_username(message.from_user.id, message.text)
    await message.answer('Имя успешно изменено! 🥳', reply_markup=kb_menu.main_menu)
    await state.clear()


# Обработчик нажатия на кнопку "Изменить номер телефона"
@user_data_edit_router.message(F.text == 'Изменить номер телефона 📲')
async def phone_number_changing(message: Message, state: FSMContext):
    await state.set_state(st.UserEditing.phone_number)
    await message.answer('Введите новое номер:')


# Обработчик состояния изменения номера телефона
@user_data_edit_router.message(st.UserEditing.phone_number)
async def number_update(message: Message, state: FSMContext):
    await rq.update_phone_number(message.from_user.id, message.text)
    await message.answer('Номер успешно изменен! 🥳', reply_markup=kb_menu.main_menu)
    await state.clear()


# Обработчик состояния нажатия на кнопку "Удалить аккаунт"
@user_data_edit_router.message(F.text == 'Удалить аккаунт ❌')
async def account_deleting(message: Message):
    await rq.delete_user(message.from_user.id)
    await message.answer('Ваш аккаунт удален...', reply_markup=kb.start_keyboard)
