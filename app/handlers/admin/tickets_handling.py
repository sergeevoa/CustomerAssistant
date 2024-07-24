"""Здесь расположены обработчики команд, callback-ов и состояний, связанных с обработкой пользовательских запросов"""

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext          # Класс для управления состояниями пользователя

import app.keyboards.admin.tickets_handling as kb
import app.keyboards.admin.main_menu as kb_main
import app.states as st
import app.database.requests.users as rq_usr
import app.database.requests.tickets as rq_tick
import app.filters as flt

from app.handlers.admin.main_menu import cmd_start

adm_ticket_router = Router()  # router выполняет функцию обработчика (Dispatcher) вне файла с точкой входа в приложение
adm_ticket_router.message.filter(flt.CheckAdmin())
adm_ticket_router.callback_query.filter(flt.CheckAdmin())


# Обработчик вывода списка пользовательских запросов
@adm_ticket_router.message(F.text == 'Вывести список запросов 🔍')
async def get_tickets(message: Message):
    await message.answer('Пользовательские запросы:', reply_markup=await kb.all_tickets())


# Обработчик нажатия на кнопку пользовательского запроса
@adm_ticket_router.callback_query(F.data.startswith('ticket_'))
async def ticket_answer(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.TicketAnswer.answer)                           # Установка состояния ответа на запрос
    await callback.answer('Вы выбрали запрос')
    ticket = await rq_tick.get_ticket(int(callback.data.split('_')[1]))   # Получение пользовательского запроса по id
    user = await rq_usr.get_user_by_id(ticket.user_id)                 # Получение объекта пользователя
    await state.update_data(user_tg_id=user.tg_id)              # Сохранение состояния пользователя для ответа ему
    await state.update_data(ticket_id=ticket.id)                # Сохранение id запроса для его последующего удаления
    # Вывод запроса в сообщении
    await callback.message.answer(f'Запрос: {ticket.text}\n\n{user.username} | {user.phone_number}\n\nНапишите ответ 📝',
                                  reply_markup=kb.ticket_exit)


# Обработчик состояния ответа на пользовательский запрос:
@adm_ticket_router.message(st.TicketAnswer.answer)
async def send_answer(message: Message, state: FSMContext, bot: Bot):
    info = await state.get_data()                                               # Получение id пользователя из состояния
    await bot.send_message(chat_id=info["user_tg_id"], text=message.text)       # Отправка сообщения пользователю по id
    await message.answer('Сообщение отправлено 🦉', reply_markup=kb_main.admin_menu)
    await rq_tick.delete_ticket(info["ticket_id"])                                      # Удаление этого запроса из БД
    await state.clear()


# Обработчик нажатия на кнопку "Назад" из просмотра пользовательского запроса
@adm_ticket_router.callback_query(F.data == 'to_ticket_list')
async def back_from_ticket(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы переходите назад')
    await state.clear()
    await get_tickets(callback.message)


# Обработчик нажатия на inline-кнопку выхода в главное меню
@adm_ticket_router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы переходите в главное меню')
    await cmd_start(callback.message, state)

