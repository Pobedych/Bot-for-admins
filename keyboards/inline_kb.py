from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def up_balance():
    inline_kb = [
        [InlineKeyboardButton(text="Поменять баланс", callback_data="change_balance")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data='delete_user')],
        [InlineKeyboardButton(text="На главную🏠", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def change_balance(balance: float):
    inline_kb = [
        [InlineKeyboardButton(text="Увеличить💲", callback_data="up_balance")],
        [InlineKeyboardButton(text="Уменьшить💲", callback_data="down_balance")],
    ]
    if balance == 0.0:
        inline_kb.append([InlineKeyboardButton(text="Обновить баланс💲", callback_data="update_balance")])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)