"""Здесь находятся обработчики, связанные с редактированием категорий блюд"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.meal_categories as kb
import app.keyboards.multi_role as kb_m
import app.states as st
import app.database.requests.meals as rq_m
import app.database.requests.restaurants as rq_r
import app.database.requests.meal_categories as rq
import app.filters as flt

from app.keyboards.admin.database_editing.restaurants import back_to_restaurant_meal_categories

meal_cat_router = Router()
meal_cat_router.message.filter(flt.CheckAdmin())
meal_cat_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Категории Блюд" из меню редактирования ресторанов
@meal_cat_router.callback_query(F.data.startswith('meal_categories_editing_'))
async def meal_cat_edit_start(callback: CallbackQuery):
    await callback.answer('')
    restaurant = await rq_r.get_restaurant(int(callback.data.split('_')[3]))
    await callback.message.answer(f'Категории блюд ресторана {restaurant.name} 🥡',
                                  reply_markup=await kb.meal_categories(restaurant.id))


# Обработчик нажатия на кнопку "Добавить блюдо"
@meal_cat_router.callback_query(F.data.startswith('add_meal_category_in_'))
async def meal_category_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealCategoryAddition.category_id)
    await state.update_data(restaurant_id=int(callback.data.split('_')[4]))
    await state.set_state(st.MealCategoryAddition.name)
    await callback.message.edit_text('Введите название категории 🥡')


# Обработчик состояния ввода названия категории
@meal_cat_router.message(st.MealCategoryAddition.name)
async def name_input(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.MealCategoryAddition.picture_link)
    await message.answer('Отлично!\nТеперь отправьте фото категории 📸')


# Обработчик состояния получения ссылки на фото категории
@meal_cat_router.message(F.photo, st.MealCategoryAddition.picture_link)
async def get_picture_link(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.add_meal_category(data["name"], message.photo[-1].file_id, data["restaurant_id"])
    await message.answer('Категория добавлена!', reply_markup=await kb.meal_categories(data["restaurant_id"]))
    await state.clear()


# Обработчик нажатия на категорию блюда
@meal_cat_router.callback_query(F.data.startswith('ad_meal_category_'))
async def meal_category_editing(callback: CallbackQuery):
    await callback.answer('')
    meal_category = await rq.get_meal_category(int(callback.data.split('_')[3]))
    await callback.message.answer_photo(photo=meal_category.picture_link, caption=f'{meal_category.name}',
                                        reply_markup=await kb.meal_category_editing(meal_category))


# Обработчик нажатия на кнопку "Изменить данные"
@meal_cat_router.callback_query(F.data.startswith('meal_category_edit_'))
async def meal_category_data_changing(callback: CallbackQuery):
    await callback.answer('')
    category_id = int(callback.data.split('_')[3])
    await callback.message.answer('Что именно вы хотите изменить? 🤔',
                                  reply_markup=await kb.meal_category_data_choosing(category_id))


# Обработчик нажатия на кнопку "Изменить название"
@meal_cat_router.callback_query(F.data.startswith('meal_cat_name_editing_'))
async def name_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealCategoryEditing.name)
    await state.update_data(meal_category_id=int(callback.data.split('_')[4]))
    await callback.message.edit_text('Введите новое название.\nНазвание должно быть не более 30 символов ❗️')


# Обработчик состояния изменения названия категории
@meal_cat_router.message(st.MealCategoryEditing.name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_category_name(data["meal_category_id"], message.text)
    await message.answer('Название обновлено! 🦉', reply_markup=await kb.back_to_meal_category(data["meal_category_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить фото"
@meal_cat_router.callback_query(F.data.startswith('meal_cat_photo_editing_'))
async def photo_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealCategoryEditing.picture_link)
    await state.update_data(meal_category_id=int(callback.data.split('_')[4]))
    await callback.message.edit_text('Отправьте новое фото 📷')


# Обработчик состояния получения новой ссылки на фото категории блюд
@meal_cat_router.message(F.photo, st.MealCategoryEditing.picture_link)
async def update_picture_link(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_category_photo(data["meal_category_id"], message.photo[-1].file_id)
    await message.answer('Фотография обновлена! 📷🦉',
                         reply_markup=await kb.back_to_meal_category(data["meal_category_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Удалить категорию"
@meal_cat_router.callback_query(F.data.startswith('meal_category_delete_'))
async def meal_category_deleting(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    category_id = int(callback.data.split('_')[3])

    # Если в базе нет блюд этой категории
    if not await rq_m.get_first_meal_from_category(category_id):
        restaurant_id = await rq.delete_meal_category(category_id)
        await callback.message.answer('Категория успешно удалена!',
                                      reply_markup=await back_to_restaurant_meal_categories(restaurant_id))
    else:
        await state.set_state(st.MealCategoryEditing.delete)
        await state.update_data(category_id=category_id)
        await callback.message.answer('Внимание! ⚠️\nВ базе хранятся данные о блюдах, '
                                      'относящихся к этой категории.\nПри удалении категории все данные о блюдах, '
                                      'относящихся к ним, также будут удалены.'
                                      '\nВсе равно удалить категорию?', reply_markup=kb_m.yes_no)


# Обработчик нажатия на кнопку "Да" при удалении категории блюд, содержащей блюда
@meal_cat_router.message(F.text == 'Да ✅', st.MealCategoryEditing.delete)
async def delete_yes(message: Message, state: FSMContext):
    data = await state.get_data()
    restaurant_id = await rq.delete_meal_category(data["category_id"])
    await message.answer('Категория успешно удалена!',
                         reply_markup=await back_to_restaurant_meal_categories(restaurant_id))
    await state.clear()


# Обработчик нажатия на кнопку "Нет" при удалении категории блюд, содержащей блюда
@meal_cat_router.message(F.text == 'Нет ❌', st.MealCategoryEditing.delete)
async def delete_no(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Операция отменена 🦉', reply_markup=await kb.back_to_meal_category(data["category_id"]))
    await state.clear()
