"""Здесь задаются подсказки для меню команд бота в telegram чате с ним. Пользователям с различными ролями доступны
разные списки команд"""

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Запустить бота / вернуться в начало'
        ),
        BotCommand(
            command='admin_start',
            description='Запустить бота в роли администратора / вернуться в главное меню администратора'
        ),
        BotCommand(
            command='courier_start',
            description='Запустить бота в роли курьера / вернуться в главное меню курьера'
        ),
        BotCommand(
            command='manager_start',
            description='Запустить бота в роли менеджера / вернуться в главное меню менеджера'
        ),
    ]

    # Установка подсказки в меню для команд, доступных всем пользователям по умолчанию
    await bot.set_my_commands(commands, BotCommandScopeDefault())
