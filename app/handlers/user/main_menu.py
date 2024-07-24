"""Здесь находятся обработчики, связанные с выводом главного меню и возвращением в него"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.user.main_menu as kb

from app.handlers.user.registration import cmd_start


menu_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение


# Обработчик нажатия на кнопку "В главное меню"
@menu_router.message(F.text == 'В главное меню 📱')
async def to_main(message: Message, state: FSMContext):
    await cmd_start(message, state)


# Обработчик нажатия на кнопку главного меню в inline клавиатурах
@menu_router.callback_query(F.data == 'to_main')
async def to_main_inline(callback: CallbackQuery):
    await callback.answer('Вы переходите в главное меню')
    await callback.message.answer("Приветствуем Вас в *Moonkin's Food*", reply_markup=kb.main_menu)
