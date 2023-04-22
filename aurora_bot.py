import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import API_TOKEN
from config import USER_ID

GREETING = 'Bonjour!'

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
    await message.reply(GREETING)


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
        data["text"] = message.text

    await message.reply(text='', reply_markup=markup)
    await SaveText.next()


@dp.callback_query_handler(text=["remember", "ignore"], state=SaveText.waiting_for_confirmation)
async def process_callback_save(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "remember":
        async with state.proxy() as data:
            text = data["text"]
            user_id = callback_query.from_user.id
            with open(f"{user_id}.txt", "a", encoding="utf-8") as f:
                f.write(f"{text}\n")
            await bot.answer_callback_query(callback_query.id, text="Copied that, Sir!")
    else:
        await bot.answer_callback_query(callback_query.id, text="OK")
    await state.finish()


@dp.message_handler(Text(equals="Quote"))
async def get_quote(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    quote = "No quotes"
    with open(f"{user_id}.txt", "r") as f:
        lines = f.readlines()
        if len(lines) > 0:
            quote = random.choice(lines).strip()
    await bot.send_message(user_id, quote)


@dp.message_handler()
async def aurora_bot(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await message.answer(message.text)


if __name__ == '__main__':
    await bot.send_message(USER_ID, GREETING)

    dp.register_message_handler(get_quote, commands=["quote"])
    types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Quote"))

    asyncio.run(dp.start_polling())
