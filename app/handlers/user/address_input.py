"""Здесь находятся обработчики команд, callback-ов и состояний, связанных с установкой адреса пользователем"""

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext  # Класс для управления состояниями пользователя

import app.keyboards.user.order_placing as kb
import app.keyboards.multi_role as kb_m
import app.states as st
import app.filters as flt
import app.database.requests.addresses as rq_addr
import app.database.requests.users as rq_usr
import app.database.requests.administrators as rq_adm

from app.handlers.admin.database_editing.restaurants import rest_addition_end

address_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение

is_in_order = False  # Глобальная переменная, позволяющая определить, происходит ли ввод адреса во время заказа


# Обработчик состояния запроса района
@address_router.message(st.Address.district)
async def district_input(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(st.Address.street)  # Установка состояния ввода улицы
    await message.answer('Теперь укажите название вашей улицы')


# Обработчик состояния запроса улицы
@address_router.message(st.Address.street)
async def street_input(message: Message, state: FSMContext):
    await state.update_data(street=message.text)
    await state.set_state(st.Address.home)  # Установка состояния ввода дома
    await message.answer('Укажите номер дома')


# Обработчик состояния запроса номера дома
@address_router.message(st.Address.home)
async def home_input(message: Message, state: FSMContext):
    await state.update_data(home=message.text)
    # Если ввод осуществляет администратор в активной фазе
    if flt.CheckAdmin() and await rq_adm.get_admin_status(message.from_user.id):
        await rest_addition_end(message, state)                 # Значит происходит ввод ресторана
    else:
        await state.set_state(st.Address.is_it_all)  # Установка состояния вопроса
        await message.answer('Это многоквартирный дом?', reply_markup=kb_m.yes_no)


# Обработчик состояния ответа "Нет"
@address_router.message(st.Address.is_it_all, F.text == 'Нет ❌')
async def add_address_1(message: Message, state: FSMContext):
    await state.update_data(entrance=None, apartment=None)
    await address_end(message, state)


# Обработчик состояния ответа "Да"
@address_router.message(F.text == 'Да ✅', st.Address.is_it_all)
async def add_entrance(message: Message, state: FSMContext):
    await state.set_state(st.Address.entrance)  # Установка состояния ввода подъезда
    await message.answer('Укажите подъезд')


# Обработчик состояния ввода подъезда
@address_router.message(st.Address.entrance, lambda message: message.text.isdigit())
async def add_entrance(message: Message, state: FSMContext):
    await state.update_data(entrance=int(message.text))
    await state.set_state(st.Address.apartment)  # Установка состояния ввода квартиры
    await message.answer('Укажите квартиру')


# Обработчик состояния ввода квартиры
@address_router.message(st.Address.apartment, lambda message: message.text.isdigit())
async def add_apartment(message: Message, state: FSMContext):
    await state.update_data(apartment=int(message.text))
    await address_end(message, state)


# Функция записи адреса в БД
async def address_end(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await rq_usr.get_user(
        message.from_user.id)  # Получение объекта пользователя, чтобы вписать его как владельца
    await rq_addr.set_address(data["district"], data["street"], data["home"], data["entrance"], data["apartment"],
                              None, user.id)

    # Если у пользователя есть неоформленный заказ, возвращаем его в меню выбора адреса
    await message.answer('Адрес записан 📝', reply_markup=await kb.all_addresses(user.id))
    await state.clear()
