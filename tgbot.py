import asyncio
from config import token, chat_id
from main import load_news_json, check_news_update, ALL_NEWS_URL
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text

ALL_NEWS_BUTTON = "Все новости"
LAST_NEWS_BUTTON = "Последние новости"

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

def get_last_date_news(news_list_json):
    date_sort_news = sorted(news_list_json.items(), key = lambda x: datetime.strptime(x[1]['news_date'], '%d.%m.%Y'), reverse = True)[0]
    last_date = date_sort_news[1]['news_date']

    last_date_news = {}
    for current_news, current_item in news_list_json.items():
        if last_date == current_item['news_date']:
            last_date_news.update({current_news: current_item})

    return last_date_news

def print_news_in_chat(current_item):
    return f"{hbold(current_item['news_date'])}\n" \
           f"{hlink(current_item['news_title'], current_item['news_url'])}"

@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = [ALL_NEWS_BUTTON, LAST_NEWS_BUTTON]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    keyboard.add(*start_buttons)

    await message.answer("Привет! Я умею присылать уведомления о свежих новостях на сайте www.binance.com", reply_markup = keyboard)

@dp.message_handler(Text(equals = ALL_NEWS_BUTTON))
async def start(message: types.Message):
    await message.answer(hlink("Новые крипто-листинги", ALL_NEWS_URL), disable_web_page_preview = True)

@dp.message_handler(Text(equals = LAST_NEWS_BUTTON))
async def last_date_news(message: types.Message):
    for current_news, current_item in get_last_date_news(load_news_json()).items():
        await message.answer(print_news_in_chat(current_item), disable_web_page_preview = True)

async def news_update():
    while True:
        latest_news = check_news_update()

        if len(latest_news) > 0:
            for current_news, current_item in sorted(latest_news.items()):
                await bot.send_message(chat_id, print_news_in_chat(current_item), disable_web_page_preview = True)
        else:
            await bot.send_message(chat_id, "бай май шеги ба)")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(news_update())

    executor.start_polling(dp)