import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.markdown import hlink
from config import token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()


@dp.message(Command("news"))
async def cmd_start(message: types.Message):
    with open("news_dict.json") as file:
        news_dict=json.load(file)
    for k,v in sorted(news_dict.items()):
        news= f"{hlink(v['article_title'],v['article_url'])}\n"\
            f"{v['article_desc']}\n"\
            f"{v['reading_time']}"
        await message.answer(news,parse_mode="HTML")
async def main():
    await dp.start_polling(bot)
if __name__=='__main__':
    asyncio.run(main())