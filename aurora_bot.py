import logging
from random import randrange

from aiogram import Bot, Dispatcher, executor, types

from config import API_TOKEN
from config import USER_ID

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    if message.from_user.id != USER_ID:
        return
    await message.reply("Hi!\nI'm Aurora, EchoBot and Assistant!")


async def save_message(user_id: int, message_text: str):
    """Save a message to a text file."""
    with open(f"{user_id}.txt", "a") as f:
        f.write(f"{message_text}\n")


async def get_saved_message(user_id: int):
    """Get a saved message to send back to the user."""
    with open(f"{user_id}.txt", "r") as f:
        lines = f.readlines()
        if lines == 0:
            return None
        rnd = randrange(len(lines))
        i = 0
        for message in lines:
            if i == rnd:
                return message
    return None


@dp.message_handler(commands=['mem'])
async def save_quote(message: types.Message):
    """
    This handler will be called when user sends `/mem` command
    """
    if message.from_user.id != USER_ID:
        return
    user_id = message.from_user.id
    message_text = message.text
    await save_message(user_id, message_text)
    await message.reply("I remembered, Sir!")


@dp.message_handler(commands=['get'])
async def get_quote(message: types.Message):
    """
    This handler will be called when user sends `/get` command
    """
    user_id = message.from_user.id
    if message.from_user.id != USER_ID:
        return
    saved_message = await get_saved_message(user_id)
    if saved_message:
        await bot.send_message(user_id, saved_message)


@dp.message_handler()
async def aurora_bot(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await message.answer(message.text)


async def on_startup(_):
    await bot.send_message(USER_ID, 'Hi!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
