import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards.reply_kb import start_kb, new_user
from aiogram.fsm.context import FSMContext
from filters.fsm_filter import Report, Searchuser, ChangeBalanceUp, ChangeBalanceDown, Update
from utils.database import new_users, get_users, delete_user, change_balance_bal, get_id
from keyboards.inline_kb import up_balance, change_balance
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.media_group import MediaGroupBuilder
from create_bot import bot
from create_bot import admins
from utils.image_init import main
from settings.tools import admin_only


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id in admins:
        await message.answer(
            f'<b>{message.from_user.username}</b>, вы вошли как админ👤',
            reply_markup=start_kb(),
            parse_mode='html'
        )
    else:
        await message.answer(f'Привет, {message.from_user.username}')
        result = await new_users(message.from_user.id, message.from_user.username, 0)
        if result != 'Пользователь уже существует':
            for admin_id in admins:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f'Добавлен новый пользователь👍\n{message.from_user.username}\nid{message.from_user.id}'
                )



@router.message(F.text == 'Отправить отчет📜')
@admin_only
async def cmd_send_photo(message: Message, state: FSMContext):
    await state.set_state(Report.report_id)
    await message.reply('Напишите id или username пользователя')


@router.message(Report.report_id)
async def report_id(message: Message, state: FSMContext):
    global idi
    username = message.text
    try:
        if username.startswith('@'):
            data = await get_users(username[1:])
            if data == 'Ничего не найдено':
                await message.answer('Пользователь не найден', reply_markup=new_user())
                await state.clear()
            else:
                try:
                    chat_id = username[1:]
                    idi = await get_id(chat_id)
                    await message.answer("Отправьте фото")
                    await state.set_state(Report.photo1)
                except Exception:
                    await message.answer('Отправьте именно фото')
        else:
            await message.answer("❌ Введите username (@user)!")
            return
    except AttributeError:
        await message.answer("❌ Введите username (@user)!")


@router.message(Report.photo1, F.photo)
async def report_photo1(message: Message, state: FSMContext):
    global summm1, file
    try:
        photo_1 = message.photo[-1]
        file_id = photo_1.file_id
        await state.update_data(photo1=file_id)
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "utils/downloads/photo1.jpg")
        summm1 = await main("utils/downloads/photo1.jpg")
        await message.answer('Отправьте второе фото')
    except Exception:
        await message.answer('Отправьте именно фото')
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
    abs_sum = abs(summm2-summm1)
    media = MediaGroupBuilder(caption=f"Число подписчиков изменилось на {abs_sum}")
    media.add_photo(FSInputFile('utils/downloads/photo1.jpg'))
    media.add_photo(FSInputFile('utils/downloads/photo2.jpg'))
    if summm1 < summm2:
        await bot.send_media_group(chat_id=idi, media=media.build())
    elif summm2 < summm1:
        await bot.send_media_group(chat_id=idi, media=media.build())
    await message.answer("Успешно отправлено")
    await state.clear()


""" Управление юзером (Удаление и изменения баланса) """
@router.message(F.text == 'Баланс💵')
@admin_only
async def balance(message: Message, state: FSMContext):
    await state.set_state(Searchuser.name)
    await message.answer("Введите username пользователя(@user)")


@router.message(Searchuser.name)
async def user_balance(message: Message, state: FSMContext):
    username = message.text
    if username.startswith('@'):
        name_user = username[1:]
    else:
        await message.answer("❌ Введите username (@user)!")
        return
    await state.update_data(name=name_user)
    await message.answer("Сейчас поищу")
    data = await state.get_data()
    global data1, data2
    data1 = await get_users(data["name"])
    data2 = data["name"]
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
        await asyncio.sleep(2)
        if data1 == 'Ничего не найдено':
            await message.delete()
            await message.answer('Ничего не найдено', reply_markup=new_user())
        else:
            await message.delete()
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

"""Добавление нового юзера"""
@router.message(F.text == 'Добавить нового юзера')
@admin_only
async def add_user(message: Message):
    await message.answer("Чтобы добавить нового пользователя, нужно отправить ему ссылку на этого бота и пусть он нажмет кнопку старт", reply_markup=start_kb())
    

@router.message(F.text == 'На главную🏠')
@admin_only
async def back_to_main(message: Message):
    await message.answer("Вы вернулись на главную", reply_markup=start_kb())

@router.callback_query(F.data == 'back_to_main')
async def back_to_main1(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer("Вы вернулись на главную", reply_markup=start_kb())