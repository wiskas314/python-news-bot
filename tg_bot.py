import asyncio
import logging
import json
import subprocess
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.markdown import hlink
from config import token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для парсинга новостей.\n"
        "Используй команду /news для получения новостей\n"
        "Или отправь число страниц для парсинга",
    )
@dp.message(F.text.regexp(r'^\d+$'))
async def handle_pages_number(message: types.Message):
    pages = int(message.text)
    if 1 <= pages <= 20:
        await parse_and_send_news(message, pages)
    else:
        await message.answer("Пожалуйста, введите число от 1 до 20")


async def parse_and_send_news(message: types.Message, pages: int):

    parsing_msg = await message.answer(f" Парсим {pages} страниц...")

    try:

        result = subprocess.run(
            [sys.executable, "main.py", str(pages)],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:

            await parsing_msg.delete()

            with open("news_dict.json") as file:
                news_dict = json.load(file)
                if news_dict:
                    for k, v in sorted(news_dict.items()):
                        news = f"{hlink(v['article_title'], v['article_url'])}\n" \
                            f"{v['article_desc']}\n" \
                            f"{v['reading_time']}"
                        await message.answer(news, parse_mode="HTML")
    except subprocess.TimeoutExpired:
        await message.answer(" Таймаут при парсинге. Попробуйте меньше страниц.")
@dp.message(Command("news"))
async def cmd_start(message: types.Message):
    await parse_and_send_news(message, pages=5)
async def main():
    await dp.start_polling(bot)
if __name__=='__main__':
    asyncio.run(main())
