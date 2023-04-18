import logging

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


@dp.message_handler()
async def aurora_bot(message: types.Message):
    if message.from_user.id != USER_ID:
        return
    await message.answer(message.text)


async def on_startup(_):
    await bot.send_message(USER_ID, 'Hi!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
