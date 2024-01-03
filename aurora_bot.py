import asyncio
import datetime
import html
import logging
import os
import random
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from picamera import PiCamera

from config import API_TOKEN
from config import PICTURE_FILE
from config import USER_ID

if not API_TOKEN or not USER_ID or not PICTURE_FILE:
    raise ValueError("API_TOKEN, USER_ID and PICTURE_FILE must be set")

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class SaveText(StatesGroup):
    waiting_for_confirmation = State()


def get_random_quote(user_id: int):
    quote = 'No quotes'
    file_name = f'{user_id}.txt'
    try:
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    quote = random.choice(lines)
    except Exception as e:
        logging.error(f"Error opening file {file_name}: {e}")
        quote = 'Error getting quote'
    return quote


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await on_startup()


@dp.message_handler(Text(equals='Quote'))
async def get_quote(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    await bot.send_message(user_id, get_random_quote(user_id)) @ dp.message_handler(Text(equals='Quote'))


@dp.message_handler(Text(equals='Photo'))
async def get_photo(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    try:
        file = Path(PICTURE_FILE)
        if file.exists():
            os.remove(PICTURE_FILE)
        cam = PiCamera()
        cam.rotation = 270
        cam.capture(PICTURE_FILE)
        cam.close()
        with open(PICTURE_FILE, 'rb') as photo:
            await bot.send_photo(user_id, photo)
    except Exception as e:
        logging.error(f"Error getting photo: {e}")
        await bot.send_message(user_id, f'Error getting photo: {e}')


@dp.message_handler(Text(equals='Expense'))
async def get_amount_on_day(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    expense = [20000, 15000, 10000, 5000, 75000, 70000, 65000,
               60000, 55000, 50000, 45000, 40000, 35000, 30000,
               25000, 20000, 15000, 10000, 5000, 80000, 75000,
               70000, 65000, 60000, 55000, 50000, 45000, 40000,
               35000, 30000, 25000][datetime.datetime.now().day - 1]
    await bot.send_message(user_id, '{:,}'.format(expense).replace(',', ' '))


# Handler for any text message
@dp.message_handler()
async def save_text(message: types.Message, state: FSMContext):
    if message.from_user.id != USER_ID:
        return

    markup = InlineKeyboardMarkup(row_width=2)
    button_save = InlineKeyboardButton('Remember', callback_data='remember')
    button_skip = InlineKeyboardButton('Ignore', callback_data='ignore')
    markup.add(button_save, button_skip)

    async with state.proxy() as data:
        data['message'] = message

    await message.reply(text='Your command?', reply_markup=markup)
    await SaveText.next()


@dp.callback_query_handler(text=['remember', 'ignore'], state=SaveText.waiting_for_confirmation)
async def process_callback_save(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id != USER_ID:
        return
    async with state.proxy() as data:
        message = data['message']
        message_text = html.escape(message.text.replace('\n', ' '))
        await message.delete()
    if callback_query.data == 'remember':
        with open(f'{user_id}.txt', 'a', encoding='utf-8') as f:
            f.write(f'{message_text}\n')
        await bot.answer_callback_query(callback_query.id, text='Copied that, Sir!')
    else:
        await bot.answer_callback_query(callback_query.id, text='OK')
    await callback_query.message.delete()
    await state.finish()


async def send_random_quote():
    while True:
        files = [f for f in os.listdir() if os.path.isfile(f) and f.endswith('.txt')]
        for file in files:
            user_id = int(file.split('.')[0])
            await bot.send_message(user_id, get_random_quote(user_id))
        await asyncio.sleep(random.randint(16 * 60 * 60, 32 * 60 * 60))


async def on_startup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton('Expense'),
        types.KeyboardButton('Quote'),
        types.KeyboardButton('Photo')
    )
    await bot.send_message(USER_ID, 'Bonjour!', reply_markup=markup)


async def main():
    await on_startup()
    asyncio.create_task(send_random_quote())
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
