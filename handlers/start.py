from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputFile, InputMediaPhoto
from keyboards.reply_kb import start_kb, new_user
from aiogram.fsm.context import FSMContext
from filters.fsm_filter import Report, Searchuser, ChangeBalanceUp, ChangeBalanceDown, Update
from utils.database import new_users, get_users, delete_user, change_balance_bal, get_id
from keyboards.inline_kb import up_balance, change_balance
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot
import asyncio
from create_bot import admins
from utils.image_init import main

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id in admins:
        await message.answer(f'{message.from_user.username}, вы вошли как админ👤', reply_markup=start_kb())
    else:
        await message.answer(f'Привет, {message.from_user.username}')
        a = await new_users(message.from_user.id, message.from_user.username, 0)
        if a != 'Пользователь уже существует':
            await bot.send_message(chat_id=str(admins),
                               text=f'Добавлен новый пользователь👍\n{message.from_user.username}\nid{message.from_user.id}')
        else:
            pass


@router.message(F.text == 'Отправить отчет📜')
async def cmd_send_photo(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        await state.set_state(Report.report_id)
        await message.reply('Напишите id или username пользователя')
    else:
        await message.answer('У вас нет прав админа')


@router.message(Report.report_id)
async def report_id(message: Message, state: FSMContext):
    global idi
    try:
        username = message.text
        if username.startswith('@'):
            chat_id = username[1:]
        else:
            await message.answer("❌ Введите username (@user)!")
            return
        idi = await get_id(chat_id)
        await message.answer("Отправьте фото")
        await state.set_state(Report.photo1)
    except Exception:
        await message.answer('Mistake')


@router.message(Report.photo1, F.photo)
async def report_photo1(message: Message, state: FSMContext):
    global summm1, file
    photo_1 = message.photo[-1]
    file_id = photo_1.file_id
    await state.update_data(photo1=file_id)
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "utils/downloads/photo1.jpg")
    summm1 = await main("utils/downloads/photo1.jpg")
    await message.answer('Отправьте второе фото')
    await state.set_state(Report.photo2)


@router.message(Report.photo2, F.photo)
async def report_photo2(message: Message, state: FSMContext):
    photo_2 = message.photo[-1]
    file_id = photo_2.file_id
    await state.update_data(photo2=file_id)
    file1 = await bot.get_file(file_id)
    file_path = file1.file_path
    await bot.download_file(file_path, "utils/downloads/photo2.jpg")
    summm2 = await main("utils/downloads/photo2.jpg")
    if summm1 < summm2:
        bot.send_message(chat_id=idi, text=f"Подписчиков подписалось {summm2 - summm1}")
    elif summm2 < summm1:
        await bot.send_message(chat_id=idi, text=f"Подписчиков отписалось {summm1 - summm2}")
    await message.answer("Успешно отправлено")
    await state.clear()


""" Управление юзером (Удаление и изменения баланса) """
@router.message(F.text == 'Баланс💵')
async def balance(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        await state.set_state(Searchuser.name)
        await message.answer("Введите username пользователя(@user)")
    else:
        pass


@router.message(Searchuser.name)
async def user_balance(message: Message, state: FSMContext):
    name_user = message.text[1:]
    await state.update_data(name=name_user)
    await message.answer("Сейчас поищу")
    data = await state.get_data()
    global data1, data2
    data1 = await get_users(data["name"])
    data2 = data["name"]
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
        await asyncio.sleep(2)
        if data1 == 'Ничего не найдено':
            await message.answer('Ничего не найдено', reply_markup=new_user())
        else:
            await message.answer("Нашел\n"
                                 f"ID: {message.text}\n"
                                 f"Баланс: {data1}💵", reply_markup=up_balance())
    await state.clear()


@router.callback_query(F.data == 'change_balance')
async def change_balance_user(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(f"Баланс: {data1}\nПоменять баланс", reply_markup=change_balance(data1))


#Увелечение баланса
@router.callback_query(F.data == 'up_balance')
async def up_balance_user(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeBalanceUp.difference)
    await callback_query.answer()
    await callback_query.message.answer('Введите сумму на которую хотите увеличить баланс')


@router.message(ChangeBalanceUp.difference)
async def upper_balance_user(message: Message, state: FSMContext):
    try:
        await state.update_data(difference=message.text)
        data = await state.get_data()
        summ1 = int(data['difference']) + data1
        await change_balance_bal(summ1, data2)
        await state.clear()
    except ValueError:
        await message.answer("Введите числовое значение")
    await message.answer(f"Баланс изменен: {data1}💵 ➡️ {summ1}💵")
    await message.answer('Выберете действие', reply_markup=start_kb())


#Уменьшение баланса
@router.callback_query(F.data == 'down_balance')
async def down_balance_user(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeBalanceDown.difference)
    await callback_query.answer()
    await callback_query.message.answer('Введите сумму на которую хотите уменьшить баланс')


@router.message(ChangeBalanceDown.difference)
async def downer_balance_user(message: Message, state: FSMContext):
    try:
        await state.update_data(difference=message.text)
        data = await state.get_data()
        summ = data1 - int(data['difference'])
        await change_balance_bal(summ, data2)
        await state.clear()
    except ValueError:
        await message.answer("Введите числовое значение")
    await message.answer(f"Баланс изменен: {data1}💵 ➡️ {summ}💵")
    await message.answer('Выберете действие', reply_markup=start_kb())


#Обновление баланса
@router.callback_query(F.data == 'update_balance')
async def update_balance_user1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Update.update_balance)
    await callback_query.answer()
    await callback_query.message.edit_text(f"Введите текущий баланс {data2}")


@router.message(Update.update_balance)
async def update_balance_user2(message: Message, state: FSMContext):
    try:
        balance_user1 = float(message.text)
        await state.update_data(update_balance=balance_user1)
        data = await state.get_data()
        await change_balance_bal(data['update_balance'], data2)
        await state.clear()
        await message.answer(f"Баланс обновлен\n{data2}\n{data['update_balance']}💵")
    except ValueError:
        await message.answer("❌ Введите <b>ЦЕЛОЕ</b> или <b>ДЕСЯТИЧНОЕ</b> число (например, 10 или 3.14)!",
                             parse_mode="HTML")


@router.callback_query(F.data == 'delete_user')
async def delete_user_user(callback_query: CallbackQuery):
    await delete_user(data2)
    await callback_query.answer()
    await callback_query.message.answer("Пользователь удален")
    await callback_query.message.answer('Выберете действие', reply_markup=start_kb())


@router.message(F.text)
async def add_user(message: Message):
    if message.from_user.id in admins:
        if message.text == "Добавить этого пользователя" or message.text == "Добавить нового юзера":
            await message.answer(
                "Чтобы добавить нового пользователя, нужно отправить ему ссылку на этого бота и пусть он нажмет кнопку старт")
        else:
            await message.answer("Введите известную мне команду")
    else:
        await message.answer("У вас нет таких прав")
