from aiogram.fsm.state import State, StatesGroup

class Report(StatesGroup):
    report_id = State()
    photo1 = State()
    photo2 = State()

class Update(StatesGroup):
    update_balance = State()

class Searchuser(StatesGroup):
    name = State()

class ChangeBalanceUp(StatesGroup):
    difference = State()

class ChangeBalanceDown(StatesGroup):
    difference = State()