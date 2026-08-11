import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, CHANNEL_ID
from rss_fetcher import fetch_news, get_new_news
from translator import translate_news

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера (aiogram 3.7+)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Хранилище последних опубликованных новостей (в реальном проекте - БД)
last_published_link = None
posted_today = 0


def format_post(translated_news):
    """Форматирование поста для канала"""
    title = translated_news['title']
    summary = translated_news['summary']
    link = translated_news['link']
    source = translated_news['source']

    # Очистка summary от HTML
    summary = summary.replace('<br>', '\n').replace('<p>', '').replace('</p>', '')
    summary = summary[:300] + '...' if len(summary) > 300 else summary

    post = f"""
<b>📰 {title}</b>

{summary}

<a href="{link}">Читать далее</a>

Источник: {source}
    """
    return post.strip()


async def post_news():
    """Публикация новости в канал"""
    global last_published_link, posted_today

    logger.info("Проверка новых новостей...")

    news_list = get_new_news(last_published_link)

    if not news_list:
        logger.info("Нет новых новостей")
        return

    for news in news_list:
        try:
            translated = translate_news(news)

            # Проверка на дубликат
            if translated['link'] == last_published_link:
                continue

            post_text = format_post(translated)
            await bot.send_message(CHANNEL_ID, post_text)

            last_published_link = translated['link']
            posted_today += 1

            logger.info(f"Опубликовано: {translated['title'][:30]}...")

            # Задержка между постами
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")

    # Сброс счётчика в полночь
    current_hour = datetime.now().hour
    if current_hour == 0:
        posted_today = 0


async def scheduler_loop():
    """Планировщик публикаций"""
    while True:
        await asyncio.sleep(1800)  # Проверка каждые 30 минут

        current_hour = datetime.now().hour
        # Постим с 8:00 до 23:00
        if 8 <= current_hour <= 23:
            await post_news()


async def on_startup():
    """Запуск при старте"""
    logger.info("Бот запущен!")
    await bot.send_message(CHANNEL_ID, "🤖 Бот крипто-новостей активирован!\n"
                                       "Теперь я буду публиковать новости из RSS лент.")


async def main():
    dp.startup.register(on_startup)

    # Запускаем планировщик
    asyncio.create_task(scheduler_loop())

    # Удаляем webhook и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())