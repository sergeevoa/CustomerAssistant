"""Здесь прописываются точка входа в программу"""
import os
import asyncio
import logging                      # Модуль для логирования - отслеживания действий бота в консоли
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.models import async_main

import app.menu as mn

from app.handlers.user.main_menu import menu_router
from app.handlers.user.address_input import address_router
from app.handlers.user.registration import reg_router
from app.handlers.user.ticket_sending import ticket_router
from app.handlers.user.order_placing import order_router
from app.handlers.user.account_editing import user_data_edit_router
from app.handlers.user.orders_checking import order_checkout_router

from app.handlers.admin.main_menu import adm_menu_router
from app.handlers.admin.tickets_handling import adm_ticket_router
from app.handlers.admin.couriers_and_orders import courier_order_router

from app.handlers.admin.database_editing.restaurant_categories import res_cat_router
from app.handlers.admin.database_editing.restaurants import rest_router
from app.handlers.admin.database_editing.meal_categories import meal_cat_router
from app.handlers.admin.database_editing.meals import meal_router
from app.handlers.admin.database_editing.administrators import admin_edit_router
from app.handlers.admin.database_editing.couriers import courier_edit_router
from app.handlers.admin.database_editing.managers import manager_edit_router
from app.handlers.admin.database_editing.common_user_handlers import common_edit_router

from app.handlers.manager import manager_router

from app.handlers.courier import courier_router


async def main():
    await async_main()              # При запуске бота происходит создание объекта БД и моделей ее сущностей
    load_dotenv()                   # Функция необходимая для получения констант файла .env
    bot = Bot(os.getenv('TOKEN'))   # Инициализация подключения проекта к боту
    dp = Dispatcher()               # Основной роутер. Его задача - обработка входящих обновлений бота

    # Включение в dispatcher роутеров для обработчиков команд пользователя и администратора
    dp.include_routers(courier_order_router, admin_edit_router, courier_edit_router, manager_edit_router,
                       meal_router, common_edit_router, meal_cat_router, rest_router, res_cat_router,
                       adm_ticket_router, adm_menu_router, manager_router, courier_router, menu_router, address_router,
                       reg_router, ticket_router, order_router, user_data_edit_router, order_checkout_router)

    await mn.set_commands(bot)              # Включение в меню бота подсказки стандартного набора команд

    # Функция, отправляющая запросы на сервера Telegram. В случае получения ответа бот его обработает.
    # Второй аргумент позволяет боту при включении обрабатывать все сообщения пользователей, которые поступали ему,
    # когда он был выключен
    await dp.start_polling(bot, skip_updates=False)

# Запуск внутренностей функции main() только в случае запуска именно этого файла
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)     # Вывод информации о статусе бота в консоль
    try:                                        # asyncio требуется для запуска асинхронной функции внутри синхронной
        asyncio.run(main())                     # Запуск функции main()
    except KeyboardInterrupt:                   # Инструкция на случай прерывания программы с клавиатуры
        print('exit')
