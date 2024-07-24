"""Здесь содержатся клавиатуры, предназначенные для редактирования пользователей всех типов"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для выбора категории редактируемых пользователей
edit_users_role_choosing = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Администраторы 👩‍💻')],
                                                         [KeyboardButton(text='Курьеры 🚴‍♂️')],
                                                         [KeyboardButton(text='Менеджеры 👨‍💼️')]], resize_keyboard=True)


# Создание клавиатуры меню редактирования администратора
async def common_editing(user_id, role_code):
    back_callback_data = ''
    if role_code == 0:
        back_callback_data = 'administrators'
    elif role_code == 1:
        back_callback_data = 'couriers'
    elif role_code == 2:
        back_callback_data = 'managers'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить данные 📝', callback_data=f'common_edit_{user_id}')],
        [InlineKeyboardButton(text='Удалить пользователя ❌', callback_data=f'common_delete_{user_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=back_callback_data)]])
    return keyboard


# Создание клавиатуры для выбора изменяемого атрибута администратора
async def common_edit_data_choosing(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить имя 📝', callback_data=f'common_name_editing_{user_id}')],
        [InlineKeyboardButton(text='Изменить фамилию 👨', callback_data=f'common_surname_editing_{user_id}')],
        [InlineKeyboardButton(text='Изменить номер телефона 📞', callback_data=f'common_editing_number_{user_id}')],
        [InlineKeyboardButton(text='Изменить Telegram id', callback_data=f'common_tg_id_editing_{user_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'common_edit_{user_id}')]
    ])
    return keyboard
