"""Здесь расположены обработчики, связанные с главным меню администратора"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.main_menu as kb
import app.database.requests.administrators as rq
import app.filters as flt

adm_menu_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение
adm_menu_router.message.filter(flt.CheckAdmin())
adm_menu_router.callback_query.filter(flt.CheckAdmin())


# Обработчик команды start для администраторов
@adm_menu_router.message(Command('admin_start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Указание того, что админ активен для правильного ввода ресторана
    admin = await rq.get_admin(message.from_user.id)
    await rq.change_status(admin.id, True)

    await message.answer(f'Приветствую, aдминистратор {message.from_user.first_name} 🫡', reply_markup=kb.admin_menu)


# Обработчик перехода в главное меню по inline-кнопке для администраторов
@adm_menu_router.callback_query(F.data == 'adm_to_main')
async def to_main_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(f'Приветствую, aдминистратор {callback.from_user.first_name} 🫡',
                                  reply_markup=kb.admin_menu)
