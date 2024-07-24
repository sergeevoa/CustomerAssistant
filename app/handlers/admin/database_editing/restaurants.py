"""Здесь находятся обработчики, связанные с редактированием ресторанов"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.database_editing.restaurants as kb
import app.keyboards.multi_role as kb_m
import app.states as st
import app.database.requests.restaurant_categories as rq_c
import app.database.requests.addresses as rq_addr
import app.database.requests.restaurants as rq
import app.database.requests.meal_categories as rq_m_cat
import app.filters as flt

from app.keyboards.admin.database_editing.restaurant_categories import back_to_category_restaurants

rest_router = Router()
rest_router.message.filter(flt.CheckAdmin())
rest_router.callback_query.filter(flt.CheckAdmin())


# Обработчик нажатия на кнопку "Рестораны категории"
@rest_router.callback_query(F.data.startswith('restaurants_editing_'))
async def rest_edit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    category = await rq_c.get_restaurant_category(int(callback.data.split('_')[2]))
    await callback.message.answer(f'{category.name}: рестораны', reply_markup=await kb.restaurants(category.id))


# Обработчик нажатия на кнопку "Добавить ресторан"
@rest_router.callback_query(F.data.startswith('add_restaurant_in_'))
async def restaurant_addition_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.RestaurantAddition.category_id)
    await state.update_data(category_id=int(callback.data.split('_')[3]), restaurant_id=None)
    await state.set_state(st.RestaurantAddition.name)
    await callback.message.edit_text('Введите название ресторана 🏛')


# Обработчик состояния ввода названия ресторана
@rest_router.message(st.RestaurantAddition.name)
async def name_input(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.RestaurantAddition.picture_link)
    await message.answer('Отлично!\nТеперь отправьте фото ресторана, которое я покажу клиентам при его выборе 🌌')


# Обработчик состояния получения ссылки на фото ресторана
@rest_router.message(F.photo, st.RestaurantAddition.picture_link)
async def get_picture_link(message: Message, state: FSMContext):
    # Индекс -1 означает, что бот сохраняет ссылку на версию этого фото в наилучшем качестве
    await state.update_data(picture_link=message.photo[-1].file_id)
    await state.set_state(st.Address.district)
    await message.answer('Укажите адрес ресторана 🏡 \nНачнем с района')


# Обработчик состояния ввода адресов ресторана
@rest_router.message(st.RestaurantAddition.address)
async def rest_address_input(message: Message, state: FSMContext):
    await state.set_state(st.Address.district)
    await message.answer('Укажите адрес ресторана 🏡 \nНачнем с района')


# Обработчик состояния записи ресторана в БД
async def rest_addition_end(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data["restaurant_id"]:
        rest_id = await rq.add_restaurant(data["name"], data["picture_link"], data["category_id"])
        await state.update_data(restaurant_id=rest_id)
        await message.answer('Ресторан добавлен ✅')
        await rest_addition_end(message, state)
    else:
        await rq_addr.set_address(data["district"], data["street"], data["home"], None, None,
                                  data["restaurant_id"], None)
        await message.answer('Адрес ресторана записан 📝', reply_markup=await kb.add_rest_address(int(data["category_id"])))


# Обработчик нажатия на кнопку "Добавить адрес"
@rest_router.callback_query(F.data == 'another_address')
async def another_address(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.RestaurantAddition.address)
    await rest_address_input(callback.message, state)


# Обработчик нажатия на кнопку ресторана
@rest_router.callback_query(F.data.startswith('adm_restaurant_'))
async def restaurant_editing(callback: CallbackQuery):
    await callback.answer('')
    restaurant = await rq.get_restaurant(int(callback.data.split('_')[2]))
    await callback.message.answer_photo(photo=restaurant.picture_link, caption=f'{restaurant.name}\n',
                                        reply_markup=await kb.restaurant_editing(restaurant))


# Обработчик нажатия на кнопку "Изменить данные"
@rest_router.callback_query(F.data.startswith('restaurant_edit_'))
async def restaurant_data_changing(callback: CallbackQuery):
    await callback.answer('')
    restaurant_id = int(callback.data.split('_')[2])
    await callback.message.answer('Что именно вы хотите изменить? 🤔',
                                  reply_markup=await kb.restaurant_edit_data_choosing(restaurant_id))


# Обработчик нажатия на кнопку "Изменить название"
@rest_router.callback_query(F.data.startswith('rest_name_editing_'))
async def edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.RestaurantEditing.name)
    await state.update_data(restaurant_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Введите новое название.\nНазвание должно быть не более 40 символов ❗️')


# Обработчик состояния изменения названия ресторана
@rest_router.message(st.RestaurantEditing.name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_restaurant_name(data["restaurant_id"], message.text)
    await message.answer('Название обновлено! 🦉', reply_markup=await kb.back_to_restaurant(data["restaurant_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить фото"
@rest_router.callback_query(F.data.startswith('rest_photo_editing_'))
async def edit_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.RestaurantEditing.picture_link)
    await state.update_data(restaurant_id=int(callback.data.split('_')[3]))
    await callback.message.edit_text('Отправьте новое фото! 📷')


# Обработчик состояния получения новой ссылки на фото ресторана
@rest_router.message(F.photo, st.RestaurantEditing.picture_link)
async def update_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_restaurant_photo(data["restaurant_id"], message.photo[-1].file_id)
    await message.answer('Фотография обновлена! 📷🦉', reply_markup=await kb.back_to_restaurant(data["restaurant_id"]))
    await state.clear()


# Обработчик нажатия на кнопку "Изменить категорию"
@rest_router.callback_query(F.data.startswith('change_category_'))
async def edit_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.RestaurantEditing.category)
    restaurant_id = int(callback.data.split('_')[2])
    await state.update_data(restaurant_id=restaurant_id)
    await callback.message.edit_text('Выберите к какой категории будет относиться ресторан:',
                                     reply_markup=await kb.change_category(restaurant_id))


# Обработчик нажатия на кнопку выбора категории
@rest_router.callback_query(F.data.startswith('new_restaurant_category_'), st.RestaurantEditing.category)
async def update_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    new_rest_category_id = int(callback.data.split('_')[3])
    await rq.update_restaurant_category(data["restaurant_id"], new_rest_category_id)
    await callback.message.edit_text('Категория успешно обновлена!',
                                     reply_markup=await kb.back_to_restaurant(data["restaurant_id"]))
    await state.clear()


# Обработчик нажатия на кнопку удаления ресторана
@rest_router.callback_query(F.data.startswith('restaurant_delete_'))
async def delete_restaurant(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    restaurant_id = int(callback.data.split('_')[2])

    # Если в базе нет категорий блюд, привязанных к этому ресторану
    if not await rq_m_cat.get_first_category_from_restaurant(restaurant_id):
        rest_category_id = await rq.delete_restaurant(restaurant_id)
        await callback.message.answer('Ресторан успешно удален!',
                                      reply_markup=await back_to_category_restaurants(rest_category_id))
    else:
        await state.set_state(st.RestaurantEditing.delete)
        await state.update_data(restaurant_id=restaurant_id)
        await callback.message.answer('Внимание! ⚠️\nВ базе хранятся данные о категориях блюд, '
                                      'относящихся к этому ресторану.\nПри удалении ресторана все данные об этих '
                                      'категориях и о блюдах, относящихся к ним, также будут удалены.'
                                      '\nВсе равно удалить ресторан?',
                                      reply_markup=kb_m.yes_no)


# Обработчик нажатия на кнопку "Да" при удалении ресторана, содержащего категории блюд
@rest_router.message(F.text == 'Да ✅', st.RestaurantEditing.delete)
async def delete_yes(message: Message, state: FSMContext):
    data = await state.get_data()
    rest_category_id = await rq.delete_restaurant(data["restaurant_id"])
    await message.answer('Ресторан успешно удален!', reply_markup=await back_to_category_restaurants(rest_category_id))
    await state.clear()


# Обработчик нажатия на кнопку "Нет" при удалении ресторана, содержащего категории блюд
@rest_router.message(F.text == 'Нет ❌', st.RestaurantEditing.delete)
async def delete_no(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Операция отменена 🦉', reply_markup=await kb.back_to_restaurant(data["restaurant_id"]))
    await state.clear()
