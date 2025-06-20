from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def start_kb():
    kb_list = [
        [KeyboardButton(text="Отправить отчет📜"), KeyboardButton(text='Баланс💵')],
        [KeyboardButton(text="Добавить нового юзера")]
    ]
    kb = ReplyKeyboardMarkup(keyboard=kb_list, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Use menu")
    return kb

def new_user():
    kb_list = [
        [KeyboardButton(text="Добавить этого юзера")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, one_time_keyboard=True, resize_keyboard=True)