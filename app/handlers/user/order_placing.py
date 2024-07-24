"""Здесь находятся обработчики, связанные с оформлением заказа пользователем"""

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext  # Класс для управления состояниями пользователя

import app.keyboards.user.order_placing as kb
import app.keyboards.user.main_menu as kb_menu
import app.states as st
import app.filters as flt
import app.database.requests.restaurants as rq_res
import app.database.requests.meal_categories as rq_m_cat
import app.database.requests.meals as rq_m
import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.users as rq_usr
import app.database.requests.orders as rq_ord
import app.database.requests.order_collection_addresses as rq_ord_c_addr
import app.database.requests.couriers as rq_cur

maintenance = False     # Глобальная переменная, показывающая закрыт ли бот на техобслуживание

order_router = Router()


# Обработчик нажатия на кнопку "Заказать еду"
@order_router.message(F.text == 'Заказать еду 🥡')
async def restaurant_category_choosing(message: Message):
    global maintenance
    if maintenance is True:     # Если бот закрыт на техобслуживание
        await message.answer('Простите, в данный момент вы не можете заказать еду 😢\n'
                             'Бот закрыт на техобслуживание ⚙️🛠')
    else:
        if not await rq_ord.get_current_order(message.from_user.id):  # Если заказ еще не записан в БД
            await rq_ord.add_order(message.from_user.id)  # Создание объекта заказа
        await message.answer('Выберите категорию ресторана 🥣', reply_markup=await kb.all_restaurant_categories())


# Обработчик нажатия на кнопку категории ресторана
@order_router.callback_query(F.data.startswith('res_category_'))
async def restaurant_choosing(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Выберите ресторан 🏛',
                                  reply_markup=await kb.restaurants(int(callback.data.split('_')[2])))


# Обработчик нажатия на кнопку ресторана
@order_router.callback_query(F.data.startswith('restaurant_'))
async def meal_category_choosing(callback: CallbackQuery):
    await callback.answer('')
    restaurant = await rq_res.get_restaurant(int(callback.data.split('_')[1]))
    await callback.message.answer_photo(photo=restaurant.picture_link, caption=f'{restaurant.name}\n'
                                                                               f'Выберите категорию блюд',
                                        reply_markup=await kb.meal_categories(restaurant.id, restaurant.category_id)
                                        )


# Обработчик нажатия на кнопку категории блюда
@order_router.callback_query(F.data.startswith('meal_category_'))
async def meal_choosing(callback: CallbackQuery):
    await callback.answer('')
    meal_category = await rq_m_cat.get_meal_category(int(callback.data.split('_')[2]))
    await callback.message.edit_media(media=InputMediaPhoto(media=meal_category.picture_link,
                                                            caption=f'{meal_category.name}\nВыберите блюдо'),
                                      reply_markup=await kb.meals(meal_category.id, meal_category.restaurant_id))


# Обработчик нажатия на кнопку с блюдом
@order_router.callback_query(F.data.startswith('meal_'))
async def meal_order(callback: CallbackQuery):
    await callback.answer('')
    meal = await rq_m.get_meal(int(callback.data.split('_')[1]))  # Получение объекта блюда по id
    price = round(meal.price, 2)
    if meal.caloric_capacity:
        await callback.message.edit_media(media=InputMediaPhoto(media=meal.picture_link,
                                                                caption=f'{meal.name}\n\nСостав: {meal.compound}\n\n'
                                                                        f'Калорийность: {meal.caloric_capacity} ккал\n'
                                                                        f'\nЦена: {price} RUB'),
                                          reply_markup=await kb.add_to_basket(meal.id, meal.category_id))
    else:
        await callback.message.edit_media(media=InputMediaPhoto(media=meal.picture_link,
                                                                caption=f'{meal.name}\n\nСостав: {meal.compound}\n\n'
                                                                        f'Цена: {price}'),
                                          reply_markup=await kb.add_to_basket(meal.id, meal.category_id))


# Обработчик нажатия на кнопку "Добавить в корзину"
@order_router.callback_query(F.data.startswith('add_meal_'))
async def add_to_basket(callback: CallbackQuery):
    await callback.answer('')
    order = await rq_ord.get_current_order(callback.from_user.id)  # Получение объекта текущего заказа пользователя
    meal = await rq_m.get_meal(int(callback.data.split('_')[2]))  # Получение объекта выбранного блюда
    await rq_ord_m.add_ordered_meal(meal.id, order.id)  # Добавление блюда в таблицу заказанных блюд
    await rq_ord.update_order_price(order.id, meal.price)  # Увеличение суммы заказа
    await callback.message.answer('Товар добавлен в корзину!', reply_markup=kb.order_next_steps_1)


# Обработчик нажатия на кнопку "Корзина"
@order_router.message(F.text == 'Корзина 🧺')
async def basket(message: Message):
    order = await rq_ord.get_current_order(message.from_user.id)
    price = round(order.price, 2)
    await message.answer(f'Вот ваш заказ. Сумма заказа: {price}',
                         reply_markup=await kb.all_ordered_meals(order.id))


# Обработчик нажатия на кнопку блюда в корзине
@order_router.callback_query(F.data.startswith('ordered_meal_'))
async def meal_in_basket(callback: CallbackQuery):
    await callback.answer('')
    meal = await rq_m.get_meal(int(callback.data.split('_')[2]))
    price = round(meal.price, 2)
    if meal.caloric_capacity:
        await callback.message.answer_photo(photo=meal.picture_link, caption=f'{meal.name}\n\nСостав: {meal.compound}\n'
                                                                             f'\nКалорийность: {meal.caloric_capacity} ккал'
                                                                             f'\n\nСтоимость: {price} RUB',
                                            reply_markup=await kb.meal_in_basket(meal.id))
    else:
        await callback.message.answer_photo(photo=meal.picture_link, caption=f'{meal.name}\n\nСостав: {meal.compound}\n'
                                                                             f'\nКалорийность: {meal.caloric_capacity}'
                                                                             f'\n\nСтоимость: {price} RUB',
                                            reply_markup=await kb.meal_in_basket(meal.id))


# Обработчик нажатия на кнопку удаления блюда из корзины
@order_router.callback_query(F.data.startswith('delete_ordered_meal_'))
async def delete_ordered_meal(callback: CallbackQuery):
    await callback.answer('')
    order = await rq_ord.get_current_order(callback.from_user.id)  # Получение объекта заказа
    meal = await rq_m.get_meal(int(callback.data.split('_')[3]))  # Получение объекта заказанного блюда
    await rq_ord_m.delete_ordered_meal(order.id, meal.id)  # Удаление заказанного блюда
    await rq_ord.update_order_price(order.id, (-1 * meal.price))  # Уменьшение стоимости заказа
    await callback.message.answer('Блюдо удалено из корзины')


# Обработчик нажатия на кнопку "Выбрать адрес доставки"
@order_router.message(F.text.endswith('адрес доставки 🏡'))
async def choose_address(message: Message):
    user = await rq_usr.get_user(message.from_user.id)
    await message.answer('Выберите адрес:', reply_markup=await kb.all_addresses(user.id))


# Обработчик нажатия на кнопку с адресом
@order_router.callback_query(F.data.startswith('user_address_'))
async def add_address(callback: CallbackQuery):
    await callback.answer('')
    await rq_ord.update_order_address(callback.from_user.id,
                                      int(callback.data.split('_')[2]))  # Установка адреса для заказа
    await callback.message.answer('Адрес добавлен ✅', reply_markup=kb.order_next_steps_2)


# Обработчик нажатия на кнопку "Добавить адрес"
@order_router.callback_query(F.data == 'new_address')
async def new_address(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(st.Address.district)
    await callback.message.answer('Укажите новый адрес доставки 🏡 \nНачнем с района')


# Обработчик нажатия на кнопку "Добавить блюдо"
@order_router.message(F.text == 'Добавить блюдо 🍔')
async def add_meal(message: Message):
    await restaurant_category_choosing(message)


# Обработчик нажатия на кнопку "Отменить заказ"
@order_router.message(F.text == 'Отменить заказ ❌')
async def delete_order(message: Message):
    order = await rq_ord.get_current_order(message.from_user.id)
    await rq_ord.delete_order(order.id)
    await message.answer('Заказ отменен 🦉', reply_markup=kb_menu.main_menu)


# Обработчик нажатия на кнопку "Перейти к оплате"
@order_router.message(F.text == 'Перейти к оплате 💵')
async def payment(message: Message, bot: Bot, state: FSMContext):
    order = await rq_ord.get_current_order(message.from_user.id)
    ordered_meals = await rq_ord_m.get_all_ordered_meals(order.id)
    meals_names = ''
    for ordered_meal in ordered_meals:
        meal = await rq_m.get_meal(ordered_meal.meal_id)
        if meals_names != '':
            meals_names = meals_names + ', ' + meal.name
        else:
            meals_names = meals_names + meal.name
    await bot.send_invoice(                             # Отправка счета пользователю, сделавшему заказ
        chat_id=message.chat.id,                        # id чата, куда будет отправлен счет
        title=f"Заказ Moonkin's Food № {order.id}",
        description=meals_names,
        payload='Payment through a bot',                # Информация о платеже для администратора
        provider_token='381764678:TEST:87658',          # Токен ЮКассы для обработки платежей через нее
        currency='rub',
        prices=[
            LabeledPrice(
                label='К оплате',
                # Цены в LabeledPrice указываются в монетах самого мелкого номинала, поэтому надо домножать на 100
                amount=round(order.price, 2) * 100,
                # Этот параметр нужен, чтобы при пересылке счета в другой чат отображалась не кнопка оплатить,
                # а ссылка на этого бота
                start_parameter='nztcoder',
            )
        ],
        request_timeout=15
    )
    await state.set_state(st.Payment.payment)
    await state.update_data(order_id=order.id)


# Обработчик подтверждения готовности выслать пользователю продукт после оплаты
@order_router.pre_checkout_query(st.Payment.payment)
async def pre_checkout_query_handling(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработчик успешной оплаты заказа пользователем
@order_router.message(st.Payment.payment)
async def successful_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq_ord.change_order_status(data["order_id"], 1)
    await message.answer(f'Ваш заказ оформлен 🥳\nНомер заказа: {data["order_id"]}', reply_markup=kb_menu.main_menu)
    await state.clear()


# Обработчик нажатия кнопки "Назад" из меню выбора ресторана
@order_router.callback_query(F.data.startswith('to_res_categories'))
async def back_to_res_categories(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь к выбору категории ресторана')
    await callback.message.answer('Выберите категорию ресторана 🥣', reply_markup=await kb.all_restaurant_categories())


# Обработчик нажатия кнопки "Назад" из меню выбора категории блюд
@order_router.callback_query(F.data.startswith('to_restaurants'))
async def back_to_restaurants(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь к выбору ресторана')
    await restaurant_choosing(callback)


# Обработчик нажатия кнопки "Назад" из меню выбора блюда
@order_router.callback_query(F.data.endswith('_meal_category'))
async def back_to_meal_categories(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь к выбору категории блюда')
    await meal_category_choosing(callback)


# Обработчик нажатия на кнопку "Назад" из меню блюда
@order_router.callback_query(F.data.startswith('to_meals'))
async def back_to_meals(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь к выбору блюда')
    await meal_choosing(callback)


# Обработчик нажатия на кнопку "Назад" из просмотра блюда в Корзине
@order_router.callback_query(F.data.startswith('to_basket'))
async def back_to_basket(callback: CallbackQuery):
    await callback.answer('Вы возвращаетесь в Корзину')
    order = await rq_ord.get_current_order(callback.from_user.id)
    price = round(order.price, 2)
    await callback.message.answer(f'Вот ваш заказ. Сумма заказа: {price}',
                                  reply_markup=await kb.all_ordered_meals(order.id))


# Обработчик нажатия на кнопку "Закрыть бота на техобслуживание" для администратора
@order_router.message(F.text == 'Закрыть бота на техобслуживание ⚠️', flt.CheckAdmin())
async def close_bot_for_maintenance(message: Message):
    global maintenance
    if maintenance is False:
        maintenance = True
        await message.answer('⚠️ Бот закрыт на техобслуживание ⚠️\nКлиенты пока не могут оформлять новые заказы')
    else:
        await message.answer('Бот уже закрыт для заказов ❌')


# Обработчик нажатия на кнопку "Открыть бота для заказов" для администратора
@order_router.message(F.text == 'Открыть бота для заказов ✅', flt.CheckAdmin())
async def close_bot_for_maintenance(message: Message):
    global maintenance
    if maintenance is True:
        maintenance = False
        await message.answer('🥳 Бот открыт 🥳\nКлиенты могут снова оформлять новые заказы ✅')
    else:
        await message.answer('Бот уже открыт для заказов ✅')


# Обработчик нажатия на кнопку "Подтвердить доставку" в сообщении, которое приходит от курьера
@order_router.callback_query(F.data.startswith('delivery_approve_'))
async def delivery_approve(callback: CallbackQuery, bot: Bot):
    await callback.answer('Доставка подтверждена', reply_markup=kb_menu.main_menu)
    order_id = int(callback.data.split('_')[2])
    courier_id = int(callback.data.split('_')[3])
    rating = 2
    await rq_ord.change_order_status(order_id, 4)        # Отметка заказа доставленным
    order_collection_addresses = await rq_ord_c_addr.get_order_collection_addresses(order_id)
    bonus_rating = len(list(order_collection_addresses))    # Начисление курьеру бонусных очков за адреса доставки
    final_rating = rating + bonus_rating
    await rq_cur.change_rating(courier_id, final_rating)    # Увеличение рейтинга курьера за выполненный заказ
    courier = await rq_cur.get_courier_by_id(courier_id)
    await bot.send_message(chat_id=courier.tg_id, text=f'Доставка подтверждена! Ваш рейтинг увеличен на {final_rating}')
