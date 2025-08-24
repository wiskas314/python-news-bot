import asyncio
import logging
import json
import subprocess
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.markdown import hlink, hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import token
from topic import CATEGORIES
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()
class Form(StatesGroup):
    waiting_for_topic = State()
    waiting_for_pages = State()
def topics_keybord():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[],resize_keyboard=True,one_time_keyboard=True)
    row = []
    for i,topic in enumerate(CATEGORIES.keys()):
        category=CATEGORIES[topic]['eng']
        row.append(InlineKeyboardButton(text=category,callback_data=f"category_{topic}" ))
        if (i+1)%2==0:
            keyboard.inline_keyboard.append(row)
            row=[]
    if row:
        keyboard.inline_keyboard.append((row))
    return keyboard
@dp.message(Command("start"))
async def cmd_start(message: types.Message,state: FSMContext):

    await message.answer(
        "Привет! Я бот для парсинга новостей.\n"
        "Выбери нужный тебе раздел новостей\n"
        "И  число страниц для парсинга",
        reply_markup=topics_keybord()
    )
    await state.set_state(Form.waiting_for_topic)





@dp.callback_query(F.data.startswith("category_"),Form.waiting_for_topic)
async def handle_category_callback(callback: types.CallbackQuery,state: FSMContext):
    category_slug = callback.data.split('_')[1]


    if category_slug in CATEGORIES:
        await state.update_data(selected_topic=category_slug)
        await callback.message.answer(
            f" Выбрана тема: {CATEGORIES[category_slug]['eng']}\n"
            "Теперь введите количество страниц для парсинга (1-20):"
        )
        await state.set_state(Form.waiting_for_pages)
    else:
        await callback.answer(" Категория не найдена")

    await callback.answer()


@dp.message(F.text.regexp(r'^\d+$'),Form.waiting_for_pages)
async def handle_pages_number(message: types.Message,state: FSMContext):
    pages = int(message.text)
    if 1 <= pages <= 20:

        user_data = await state.get_data()
        category_slug = user_data.get('selected_topic')

        if category_slug:
            await message.answer(f" Парсим {pages} страниц категории {CATEGORIES[category_slug]['eng']}...")
            await parse_and_send_news(message, category=category_slug, pages=pages)
            await state.clear()
        else:
            await message.answer(" Ошибка: тема не выбрана")
    else:
        await message.answer(" Пожалуйста, введите число от 1 до 20")


async def parse_and_send_news(message: types.Message,category: str, pages: int):

    parsing_msg = await message.answer(f" Парсим {pages} страниц...")
    result = subprocess.run(
        [sys.executable, "main.py", category, str(pages)],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode == 0:
        await parsing_msg.delete()
    try:

        filename = f"news_{category}.json"
        with open(filename) as file:
            news_dict = json.load(file)

        if news_dict:
            category_name = CATEGORIES[category]['eng']
            await message.answer(f" {category_name}: найдено {len(news_dict)} статей")

            for k, v in sorted(news_dict.items()):
                news = f"{hlink(v['article_title'], v['article_url'])}\n" \
                       f"{v['article_desc']}\n" \
                       f" {v['reading_time']}"
                await message.answer(news, parse_mode="HTML")
        else:
            await message.answer(" Статьи не найдены в этой категории")

    except Exception as e:
        await message.answer(f" Ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)
if __name__=='__main__':
    asyncio.run(main())

