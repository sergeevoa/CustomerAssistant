"""Здесь находятся обработчики, связанные с редактированием категорий ресторанов"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.restaurant_categories as kb
import app.keyboards.multi_role as kb_m
import app.states as st
import app.database.requests.restaurant_categories as rq
import app.database.requests.restaurants as rq_r
import app.filters as flt

res_cat_router = Router()      # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение
res_cat_router.message.filter(flt.CheckAdmin())
res_cat_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Редактировать базу ресторанов"
@res_cat_router.message(F.text == 'Редактировать базу ресторанов 🏛⚙️')
async def res_edit_start(message: Message):
    await message.answer('Выберите категорию ресторанов:', reply_markup=await kb.all_restaurant_categories())


# Обработчик нажатия на кнопку "Добавить категорию ресторанов"
@res_cat_router.callback_query(F.data == 'add_res_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CategoryEditing.add_name)
    await callback.message.edit_text('Введите название категории:')


# Обработчик состояния ввода названия новой категории ресторанов
@res_cat_router.message(st.CategoryEditing.add_name)
async def enter_category_name(message: Message, state: FSMContext):
    await rq.add_restaurant_category(message.text)
    await message.answer('Категория добавлена!', reply_markup=await kb.all_restaurant_categories())
    await state.clear()


# Обработчик нажатия на категорию ресторана
@res_cat_router.callback_query(F.data.startswith('adm_res_category_'))
async def category_menu(callback: CallbackQuery):
    await callback.answer('')
    category = await rq.get_restaurant_category(int(callback.data.split('_')[3]))
    await callback.message.edit_text(category.name, reply_markup=await kb.rest_cat_editing(category.id))


# Обработчик нажатия на кнопку "Изменить название"
@res_cat_router.callback_query(F.data.startswith('rc_edit_'))
async def edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.CategoryEditing.edit_name)
    await state.update_data(category_id=int(callback.data.split('_')[2]))
    await callback.message.edit_text('Введите новое название.\nНазвание должно быть не более 40 символов ❗️')


# Обработчик состояния изменения названия
@res_cat_router.message(st.CategoryEditing.edit_name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_name(data["category_id"], message.text)
    await message.answer('Название обновлено!')
    category = await rq.get_restaurant_category(data["category_id"])
    await message.answer(category.name, reply_markup=await kb.rest_cat_editing(category.id))
    await state.clear()


# Обработчик нажатия на кнопку "Удалить категорию"
@res_cat_router.callback_query(F.data.startswith('rc_delete_'))
async def delete_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    category_id = int(callback.data.split('_')[2])

    if not await rq_r.get_first_restaurant_from_category(category_id):    # Если в базе нет ресторанов этой категории
        await rq.delete_category(category_id)
        await callback.message.answer('Категория успешно удалена!')
        await res_edit_start(callback.message)
    else:
        await state.set_state(st.CategoryEditing.delete)
        await state.update_data(category_id=category_id)
        await callback.message.answer('Внимание! ⚠️\nВ базе хранятся данные о ресторанах, '
                                      'относящихся к этой категории.\nПри удалении категории все данные об этих '
                                      'ресторанах также будут удалены.\nВсе равно удалить категорию?',
                                      reply_markup=kb_m.yes_no)


# Обработчик нажатия на кнопку "Да" при удалении категории, содержащей рестораны
@res_cat_router.message(F.text == 'Да ✅', st.CategoryEditing.delete)
async def delete_yes(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.delete_category(data["category_id"])
    await message.answer('Категория успешно удалена!')
    await state.clear()
    await res_edit_start(message)


# Обработчик нажатия на кнопку "Нет" при удалении категории, содержащей рестораны
@res_cat_router.message(F.text == 'Нет ❌', st.CategoryEditing.delete)
async def delete_no(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Операция отменена 🦉', reply_markup=await kb.back_to_rest_category(data["category_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Назад"
@res_cat_router.callback_query(F.data == 'to_res_categories_editing')
async def back_to_rest_categories(callback: CallbackQuery):
    await callback.answer('')
    await res_edit_start(callback.message)
