"""Здесь находятся обработчики команд, callback-ов и состояний, связанных с регистрацией пользователя"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.user.registration as kb
import app.keyboards.user.main_menu as kb_menu
import app.states as st
import app.database.requests.users as rq_usr
import app.database.requests.administrators as rq_adm
import app.filters as flt


reg_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение


# Если курьер пытается ввести команду start во время доставки
@reg_router.message(CommandStart(), flt.CheckCourier(), st.CourierOrderDeliver.delivering)
async def block_courier_enter(message: Message):
    await message.answer('Вы не можете войти в качестве пользователя пока идет доставка! ❌')


# Обработчик пользовательской команды start для админов
@reg_router.message(CommandStart(), flt.CheckAdmin())
async def cmd_start_for_admins(message: Message, state: FSMContext):
    await state.clear()
    # Указание на то, что администратор неактивен, если вошел как пользователь,
    # для корректного ввода адреса доставки
    admin = await rq_adm.get_admin(message.from_user.id)
    await rq_adm.change_status(admin.id, False)
    await register_check(message)


# Обработчик команды start
@reg_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await register_check(message)


# Функция проверки регистрации пользователя
async def register_check(message: Message):
    # Проверка регистрации пользователя
    if not await rq_usr.get_user(message.from_user.id):  # Если пользователь не зарегистрирован
        # Вывод предложения о регистрации и регистрационной клавиатуры
        await message.answer('Приветствуем вас в нашем сервисе! Чтобы воспользоваться его функциями \n\n '
                             'Зарегистрируйтесь ⬇️', reply_markup=kb.register_kb)
    else:
        # Если пользователь зарегистрирован, происходит вход в главное меню
        await message.answer('Приветствуем Вас в *Customer_Assistant*', reply_markup=kb_menu.main_menu)


# Обработчик нажатия кнопки "Зарегистрироваться"
@reg_router.callback_query(F.data == 'register')
async def reg_start(callback: CallbackQuery, state: FSMContext):
    # callback должен получить ответ на сервер, чтобы нажатая кнопка перестала гореть
    await callback.answer('')
    await state.set_state(st.Reg.number)             # Установка состояния ввода номера телефона
    # Вывод клавиатуры с кнопкой по которой можно в один клик направить боту свой номер телефона
    await callback.message.answer('Укажите номер телефона ☎️', reply_markup=kb.get_number)


# Обработчик состояния запроса номера телефона
@reg_router.message(st.Reg.number, F.contact)
async def number_input(message: Message, state: FSMContext):
    # Из последнего сообщения пользователя считывается номер и записывается как поле объекта state
    await state.update_data(number=message.contact.phone_number)
    await state.set_state(st.Reg.name)                      # Установка состояния ввода имени пользователя
    await message.answer('Введите ваше имя')


# Обработчик состояния запроса имени пользователя
@reg_router.message(st.Reg.name)
async def name_input(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Записываем информацию из state в переменную. Информация представлена в виде словаря.
    data = await state.get_data()
    # Отправка запроса на создание объекта пользователя в БД
    await rq_usr.register_user(data["name"], data["number"], message.from_user.id)
    await message.answer(f'Приветствую вас, {data["name"]}', reply_markup=kb_menu.main_menu)
    await state.clear()
