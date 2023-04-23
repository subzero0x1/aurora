import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import API_TOKEN
from config import USER_ID

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class SaveText(StatesGroup):
    waiting_for_confirmation = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await on_startup()


@dp.message_handler(Text(equals="Quote"))
async def send_quote(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    quote = "No quotes"
    file_name = f"{user_id}.txt"
    if os.path.isfile(file_name):
        with open(f"{user_id}.txt", "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                quote = random.choice(lines).strip()
    await bot.send_message(user_id, quote)


# Handler for any text message
@dp.message_handler()
async def save_text(message: types.Message, state: FSMContext):
    if message.from_user.id != USER_ID:
        return

    markup = InlineKeyboardMarkup(row_width=2)
    button_save = InlineKeyboardButton("Remember", callback_data="remember")
    button_skip = InlineKeyboardButton("Ignore", callback_data="ignore")
    markup.add(button_save, button_skip)

    async with state.proxy() as data:
        data["message"] = message

    await message.reply(text='Your command?', reply_markup=markup)
    await SaveText.next()


@dp.callback_query_handler(text=["remember", "ignore"], state=SaveText.waiting_for_confirmation)
async def process_callback_save(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id != USER_ID:
        return
    async with state.proxy() as data:
        message = data["message"]
        message_text = message.text
        await message.delete()
    if callback_query.data == "remember":
        with open(f"{user_id}.txt", "a", encoding="utf-8") as f:
            f.write(f"{message_text}\n")
        await bot.answer_callback_query(callback_query.id, text="Copied that, Sir!")
    else:
        await bot.answer_callback_query(callback_query.id, text="OK")
    await callback_query.message.delete()
    await state.finish()


@dp.message_handler()
async def aurora_bot(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await message.answer(message.text)


async def on_startup():
    dp.register_message_handler(send_quote, commands=["quote"])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Quote"))
    await bot.send_message(USER_ID, 'Bonjour!', reply_markup=markup)


if __name__ == '__main__':
    asyncio.run(on_startup())
    asyncio.run(dp.start_polling())
