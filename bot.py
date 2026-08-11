import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, ContextTypes, JobQueue

from config import BOT_TOKEN, CHANNEL_ID
from rss_fetcher import fetch_news, get_new_news
from translator import translate_news

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище последних опубликованных новостей
last_published_link = None
posted_today = 0


def format_post(translated_news):
    """Форматирование поста для канала"""
    title = translated_news['title']
    summary = translated_news['summary']
    link = translated_news['link']
    source = translated_news['source']

    summary = summary.replace('<br>', '\n').replace('<p>', '').replace('</p>', '')
    summary = summary[:300] + '...' if len(summary) > 300 else summary

    post = f"""
📰 <b>{title}</b>

{summary}

<a href="{link}">Читать далее</a>

Источник: {source}
    """
    return post.strip()


async def post_news(bot: Bot):
    """Публикация новости в канал"""
    global last_published_link, posted_today

    logger.info("Проверка новых новостей...")

    news_list = get_new_news(last_published_link)

    if not news_list:
        logger.info("Нет новых новостей")
        return

    for news in news_list[:3]:
        try:
            translated = translate_news(news)

            if translated['link'] == last_published_link:
                continue

            post_text = format_post(translated)
            await bot.send_message(CHANNEL_ID, post_text, parse_mode='HTML')

            last_published_link = translated['link']
            posted_today += 1

            logger.info(f"Опубликовано: {translated['title'][:30]}...")

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")


async def scheduler_job(context: ContextTypes.DEFAULT_TYPE):
    """Планировщик публикаций"""
    current_hour = datetime.now().hour
    if 8 <= current_hour <= 23:
        await post_news(context.bot)


async def post_startup(app: Application):
    """Запуск при старте"""
    logger.info("Бот запущен!")
    await app.bot.send_message(CHANNEL_ID, "🤖 Бот крипто-новостей активирован!\n"
                                            "Теперь я буду публиковать новости из RSS лент.")


async def main():
    job_queue = JobQueue()
    app = Application.builder().token(BOT_TOKEN).job_queue(job_queue).build()

    # Startup
    await post_startup(app)

    # Планировщик каждые 30 минут
    app.job_queue.run_repeating(scheduler_job, interval=1800, first=10)

    # Запуск
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())