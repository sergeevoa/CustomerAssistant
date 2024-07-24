"""Здесь находятся обработчики, связанные с редактированием пользователей всех ролей"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.states as st
import app.filters as flt

import app.database.requests.administrators as rq_adm
import app.database.requests.couriers as rq_cur
import app.database.requests.managers as rq_man

from app.database.requests.orders import get_first_courier_not_completed_order

import app.keyboards.admin.database_editing.administrators as kb_adm
import app.keyboards.admin.database_editing.couriers as kb_cur
import app.keyboards.admin.database_editing.managers as kb_man
import app.keyboards.admin.database_editing.common_user_keyboards as kb


common_edit_router = Router()
common_edit_router.message.filter(flt.CheckAdmin())
common_edit_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Редактировать базу пользователей"
@common_edit_router.message(F.text == 'Редактировать базу пользователей 👨⚙️')
async def user_edit_start(message: Message):
    await message.answer('Базу пользователей какой роли вы хотите редактировать?',
                         reply_markup=kb.edit_users_role_choosing)


# Обработчик состояния ввода имени пользователя
@common_edit_router.message(st.CommonUserAddition.name)
async def name_input(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.CommonUserAddition.surname)
    await message.answer('Введите фамилию')


# Обработчик состояния ввода фамилии пользователя
@common_edit_router.message(st.CommonUserAddition.surname)
async def surname_input(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(st.CommonUserAddition.phone_number)
    await message.answer('Введите номер телефона')


# Обработчик состояния ввода номера телефона
@common_edit_router.message(st.CommonUserAddition.phone_number)
async def phone_number_input(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(st.CommonUserAddition.tg_id)
    await message.answer('Введите Telegram id')


# Обработчик состояния ввода Telegram id
@common_edit_router.message(st.CommonUserAddition.tg_id, lambda message: message.text.isdigit())
async def tg_id_input(message: Message, state: FSMContext):
    await state.update_data(tg_id=int(message.text))
    data = await state.get_data()
    if data["role"] == 0:
        await rq_adm.add_admin(data["name"], data["surname"], data["phone_number"], data["tg_id"])
        await message.answer('Администратор добавлен!', reply_markup=await kb_adm.administrators())
    elif data["role"] == 1:
        await rq_cur.add_courier(data["name"], data["surname"], data["phone_number"], data["tg_id"])
        await message.answer('Курьер добавлен!', reply_markup=await kb_cur.couriers())
    elif data["role"] == 2:
        await rq_man.add_manager(data["name"], data["surname"], data["phone_number"], data["tg_id"],
                                 data["restaurant_id"])
        await message.answer('Менеджер добавлен!', reply_markup=await kb_man.managers(data["restaurant_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить данные"
@common_edit_router.callback_query(F.data.startswith('common_edit_'), st.CommonUserEditing.role)
async def data_editing(callback: CallbackQuery):
    await callback.answer('')
    user_id = int(callback.data.split('_')[2])
    await callback.message.answer('Что именно вы хотите изменить? 🤔',
                                  reply_markup=await kb.common_edit_data_choosing(user_id))


# Обработчик нажатия на кнопку "Изменить имя"
@common_edit_router.callback_query(F.data.startswith('common_name_editing_'))
async def name_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.name)
    await state.update_data(user_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новое имя (не более 30 символов)')


# Обработчик состояния изменения имени пользователя
@common_edit_router.message(st.CommonUserEditing.name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["role"] == 0:
        await rq_adm.change_name(data["user_id"], message.text)
        await message.answer('Имя изменено!', reply_markup=await kb_adm.back_to_admin(data["user_id"]))
    elif data["role"] == 1:
        await rq_cur.change_name(data["user_id"], message.text)
        await message.answer('Имя изменено!', reply_markup=await kb_cur.back_to_courier(data["user_id"]))
    elif data["role"] == 2:
        await rq_man.change_name(data["user_id"], message.text)
        await message.answer('Имя изменено!', reply_markup=await kb_man.back_to_manager(data["user_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить фамилию"
@common_edit_router.callback_query(F.data.startswith('common_surname_editing_'))
async def surname_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.surname)
    await state.update_data(user_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новую фамилию (не более 30 символов)')


# Обработчик состояния изменения фамилии пользователя
@common_edit_router.message(st.CommonUserEditing.surname)
async def update_surname(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["role"] == 0:
        await rq_adm.change_surname(data["user_id"], message.text)
        await message.answer('Фамилия изменена!', reply_markup=await kb_adm.back_to_admin(data["user_id"]))
    elif data["role"] == 1:
        await rq_cur.change_surname(data["user_id"], message.text)
        await message.answer('Фамилия изменена!', reply_markup=await kb_cur.back_to_courier(data["user_id"]))
    elif data["role"] == 2:
        await rq_man.change_surname(data["user_id"], message.text)
        await message.answer('Фамилия изменена!', reply_markup=await kb_man.back_to_manager(data["user_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить номер телефона"
@common_edit_router.callback_query(F.data.startswith('common_editing_number_'))
async def number_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.phone_number)
    await state.update_data(user_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новый номер телефона')


# Обработчик состояния изменения номера телефона
@common_edit_router.message(st.CommonUserEditing.phone_number)
async def update_number(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["role"] == 0:
        await rq_adm.change_number(data["user_id"], message.text)
        await message.answer('Номер изменен!', reply_markup=await kb_adm.back_to_admin(data["user_id"]))
    elif data["role"] == 1:
        await rq_cur.change_number(data["user_id"], message.text)
        await message.answer('Номер изменен!', reply_markup=await kb_cur.back_to_courier(data["user_id"]))
    elif data["role"] == 2:
        await rq_man.change_number(data["user_id"], message.text)
        await message.answer('Номер изменен!', reply_markup=await kb_man.back_to_manager(data["user_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить Telegram id"
@common_edit_router.callback_query(F.data.startswith('common_tg_id_editing_'))
async def tg_id_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CommonUserEditing.tg_id)
    await state.update_data(user_id=int(callback.data.split('_')[4]))
    await callback.message.edit_text('Введите новый id')


# Обработчик состояния изменения Telegram id пользователя
@common_edit_router.message(st.CommonUserEditing.tg_id, lambda message: message.text.isdigit())
async def update_tg_id(message: Message, state: FSMContext):
    data = await state.get_data()
    new_tg_id = int(message.text)
    if data["role"] == 0:
        await rq_adm.change_tg_id(data["user_id"], new_tg_id)
        await message.answer('Telegram id изменен!', reply_markup=await kb_adm.back_to_admin(data["user_id"]))
    elif data["role"] == 1:
        await rq_cur.change_tg_id(data["user_id"], new_tg_id)
        await message.answer('Telegram id изменен!', reply_markup=await kb_cur.back_to_courier(data["user_id"]))
    elif data["role"] == 2:
        await rq_man.change_tg_id(data["user_id"], new_tg_id)
        await message.answer('Telegram id изменен!', reply_markup=await kb_man.back_to_manager(data["user_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Удалить пользователя"
@common_edit_router.callback_query(F.data.startswith('common_delete_'), st.CommonUserEditing.role)
async def delete_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    user_id = int(callback.data.split('_')[2])
    if data["role"] == 0:
        await rq_adm.delete_admin(user_id)
        await callback.message.edit_text('Администратор удален!', reply_markup=await kb_adm.administrators())
    elif data["role"] == 1:
        if not await get_first_courier_not_completed_order(user_id):
            await rq_cur.delete_courier(user_id)
            await callback.message.edit_text('Курьер удален!',
                                             reply_markup=await kb_cur.couriers())
        else:
            await callback.message.edit_text('Невозможно удалить этого курьера, так как он в данный момент выполняет '
                                             'заказ ❌', reply_markup=await kb_cur.couriers())
    elif data["role"] == 2:
        manager = await rq_man.get_manager_by_id(user_id)
        restaurant_id = manager.restaurant_id
        await rq_man.delete_manager(user_id)
        await callback.message.edit_text('Менеджер удален!',
                                         reply_markup=await kb_man.managers(restaurant_id))
    await state.clear()
