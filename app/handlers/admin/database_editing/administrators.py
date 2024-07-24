"""Здесь находятся обработчики, связанные с редактированием администраторов"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.administrators as kb
import app.keyboards.admin.database_editing.common_user_keyboards as kb_c
import app.states as st
import app.database.requests.administrators as rq
import app.filters as flt

admin_edit_router = Router()
admin_edit_router.message.filter(flt.CheckAdmin())
admin_edit_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Администраторы"
@admin_edit_router.message(F.text == 'Администраторы 👩‍💻')
async def admin_edit_start(message: Message):
    await message.answer(f'Список администраторов 👩‍💻:', reply_markup=await kb.administrators())


# Обработчик нажатия на кнопку "Добавить администратора"
@admin_edit_router.callback_query(F.data.startswith('add_admin'))
async def admin_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserAddition.role)
    await state.update_data(role=0)
    await state.set_state(st.CommonUserAddition.name)
    await callback.message.edit_text('Введите имя')


# Обработчик состояния нажатия на кнопку администратора
@admin_edit_router.callback_query(F.data.startswith('admin_'))
async def admin_editing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.role)
    await state.update_data(role=0)
    admin = await rq.get_admin_by_id(int(callback.data.split('_')[1]))
    await callback.message.edit_text(f'Администратор № {admin.id}:\n{admin.name} {admin.surname}\n'
                                     f'Номер телефона: {admin.phone_number}\nTelegram id: {admin.tg_id}',
                                     reply_markup=await kb_c.common_editing(admin.id, 0))


# Обработчик нажатия на кнопку "Назад" из меню просмотра администратора
@admin_edit_router.callback_query(F.data == 'administrators')
async def to_admin_list(callback: CallbackQuery):
    await callback.answer('')
    await admin_edit_start(callback.message)
