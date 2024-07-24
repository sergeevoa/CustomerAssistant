"""Здесь находятся обработчики, связанные с редактированием блюд"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.meals as kb
import app.states as st
import app.database.requests.meals as rq
import app.database.requests.meal_categories as rq_m_cat
import app.database.requests.ordered_meals as rq_ord_m
import app.filters as flt

from app.keyboards.admin.database_editing.meal_categories import back_to_category_meals

meal_router = Router()
meal_router.message.filter(flt.CheckAdmin())
meal_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Блюда категории"
@meal_router.callback_query(F.data.startswith('meals_editing_'))
async def meal_edit_start(callback: CallbackQuery):
    await callback.answer('')
    category = await rq_m_cat.get_meal_category(int(callback.data.split('_')[2]))
    await callback.message.answer(f'Блюда категории {category.name}', reply_markup=await kb.meals(category.id))


# Обработчик нажатия на кнопку "Добавить блюдо"
@meal_router.callback_query(F.data.startswith('add_meal_in_'))
async def meal_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealAddition.category_id)
    await state.update_data(category_id=int(callback.data.split('_')[3]))
    await state.set_state(st.MealAddition.name)
    await callback.message.edit_text('Введите название блюда 🍔')


# Обработчик состояния ввода названия блюда
@meal_router.message(st.MealAddition.name)
async def name_input(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.MealAddition.picture_link)
    await message.answer('Отлично!\nТеперь отправьте фото блюда, которое я буду показывать всем клиентам! 🍔📸')


# Обработчик состояния получения ссылки на фото ресторана
@meal_router.message(F.photo, st.MealAddition.picture_link)
async def get_picture_link(message: Message, state: FSMContext):
    await state.update_data(picture_link=message.photo[-1].file_id)
    await state.set_state(st.MealAddition.compound)
    await message.answer('Напишите из чего состоит блюдо 🍋🍊🥬')


# Обработчик состояния ввода состава блюда
@meal_router.message(st.MealAddition.compound)
async def compound_input(message: Message, state: FSMContext):
    await state.update_data(compound=message.text)
    await state.set_state(st.MealAddition.caloric_capacity)
    await message.answer('Укажите калорийность блюда в расчете на 100г', reply_markup=kb.caloric_capacity_input_choice)


# Обработчик состояния ввода калорийности блюда
@meal_router.message(st.MealAddition.caloric_capacity, lambda message: message.text.isdigit())
async def caloric_capacity_input(message: Message, state: FSMContext):
    await state.update_data(caloric_capacity=float(message.text))
    await price_input_start(message, state)


# Обработчик состояния ввода калорийности блюда при отказе ее вводить
@meal_router.message(st.MealAddition.caloric_capacity, F.text == 'Не указывать калорийность')
async def no_caloric_capacity(message: Message, state: FSMContext):
    await state.update_data(caloric_capacity=None)
    await price_input_start(message, state)


# Функция, помещающая пользователя в состояние ввода цены блюда
async def price_input_start(message: Message, state: FSMContext):
    await state.set_state(st.MealAddition.price)
    await message.answer('Укажите цену блюда 💵')


# Обработчик состояния ввода цены блюда
@meal_router.message(st.MealAddition.price, lambda message: message.text.isdigit())
async def price_input(message: Message, state: FSMContext):
    data = await state.get_data()
    category = await rq_m_cat.get_meal_category(data["category_id"])
    await rq.add_meal(data["name"], data["compound"], data["caloric_capacity"],
                      float(message.text), data["picture_link"], category.id, category.restaurant_id)
    await message.answer('Блюдо добавлено! 🦉', reply_markup=await kb.meals(int(data["category_id"])))


# Обработчик нажатия на кнопку блюда
@meal_router.callback_query(F.data.startswith('adm_meal_'))
async def meal_editing(callback: CallbackQuery):
    await callback.answer('')
    meal = await rq.get_meal(int(callback.data.split('_')[2]))
    if meal.caloric_capacity:
        await callback.message.answer_photo(photo=meal.picture_link, caption=f'{meal.name}\n\nСостав: {meal.compound}\n'
                                                                             f'\nКалорийность: {meal.caloric_capacity} ккал'
                                                                             f'\n\nСтоимость: {meal.price} RUB',
                                            reply_markup=await kb.meal_editing(meal))
    else:
        await callback.message.answer_photo(photo=meal.picture_link, caption=f'{meal.name}\n\nСостав: {meal.compound}\n'
                                                                             f'\n\nСтоимость: {meal.price} RUB',
                                            reply_markup=await kb.meal_editing(meal))


# Обработчик нажатия на кнопку "Изменить данные"
@meal_router.callback_query(F.data.startswith('adm_edit_'), F.data.endswith('_meal'))
async def meal_data_changing(callback: CallbackQuery):
    await callback.answer('')
    meal_id = int(callback.data.split('_')[2])
    # Если это блюдо относится к заказанным в активных заказах
    if await rq_ord_m.is_this_meal_in_active_orders(meal_id):
        await callback.message.answer('Редактирование информации о блюде невозможно! ❌'
                                      '\nДанное блюдо сейчас присутствует среди активных заказов.')
        await meal_editing(callback)
    else:
        await callback.message.answer('Что именно вы хотите изменить? 🤔',
                                      reply_markup=await kb.meal_edit_data_choosing(meal_id))


# Обработчик нажатия на кнопку "Изменить название"
@meal_router.callback_query(F.data.startswith('name_editing_meal_'))
async def name_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealEditing.name)
    await state.update_data(meal_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новое название.\nНазвание должно быть не более 30 символов ❗️')


# Обработчик состояния изменения названия блюда
@meal_router.message(st.MealEditing.name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_name(data["meal_id"], message.text)
    await message.answer('Название обновлено! 🦉', reply_markup=await kb.back_to_meal(data["meal_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить фото"
@meal_router.callback_query(F.data.startswith('photo_editing_meal_'))
async def photo_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealEditing.picture_link)
    await state.update_data(meal_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Отправьте новое фото! 📷')


# Обработчик состояния получения новой ссылки на фото блюда
@meal_router.message(F.photo, st.MealEditing.picture_link)
async def update_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_photo(data["meal_id"], message.photo[-1].file_id)
    await message.answer('Фотография обновлена! 📷🦉', reply_markup=await kb.back_to_meal(data["meal_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить состав"
@meal_router.callback_query(F.data.startswith('compound_editing_meal_'))
async def compound_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealEditing.compound)
    await state.update_data(meal_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Напишите новый состав блюда 🍋🍊🥬')


# Обработчик состояния изменения состава блюда
@meal_router.message(st.MealEditing.compound)
async def update_compound(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_compound(data["meal_id"], message.text)
    await message.answer('Состав обновлен! 🦉', reply_markup=await kb.back_to_meal(data["meal_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить калорийность"
@meal_router.callback_query(F.data.startswith('caloric_capacity_editing_'))
async def caloric_capacity_changing(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.MealEditing.caloric_capacity)
    await state.update_data(meal_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Укажите новое значение калорийности ⚖️')


# Обработчик состояния изменения калорийности
@meal_router.message(st.MealEditing.caloric_capacity, lambda message: message.text.isdigit())
async def update_caloric_capacity(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_caloric_capacity(data["meal_id"], int(message.text))
    await message.answer('Значение калорийности обновлено! 🦉', reply_markup=await kb.back_to_meal(data["meal_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить цену"
@meal_router.callback_query(F.data.startswith('price_editing_meal_'))
async def price_changing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.MealEditing.price)
    await state.update_data(meal_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новую цену 💵')


# Обработчик состояния изменения цены
@meal_router.message(st.MealEditing.price)
async def update_price(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_meal_price(data["meal_id"], float(message.text))
    await message.answer('Стоимость обновлена! 🦉', reply_markup=await kb.back_to_meal(data["meal_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Удалить блюдо"
@meal_router.callback_query(F.data.startswith('adm_delete_'), F.data.endswith('_meal'))
async def delete_meal(callback: CallbackQuery):
    await callback.answer('')
    meal_id = int(callback.data.split('_')[2])
    # Если это блюдо относится к заказанным в активных заказах
    if await rq_ord_m.is_this_meal_in_active_orders(meal_id):
        await callback.message.answer('Удаление информации о блюде невозможно! ❌'
                                      '\nДанное блюдо сейчас присутствует среди активных заказов.')
        await meal_editing(callback)
    else:
        meal_category_id = await rq.delete_meal(meal_id)
        await callback.message.answer('Блюдо успешно удалено! 🦉',
                                      reply_markup=await back_to_category_meals(meal_category_id))
