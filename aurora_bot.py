import logging

from aiogram import Bot, Dispatcher, executor, types

# t.me/aurora_personal_assistant_bot

API_TOKEN = ''

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
    if message.from_user.id != 1:
        return
    await message.reply("Hi!\nI'm Aurora, EchoBot!")


@dp.message_handler()
async def aurora_bot(message: types.Message):
    if message.from_user.id != 1:
        return
    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
