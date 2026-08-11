import os
from dotenv import load_dotenv

load_dotenv()

# Конфигурация бота (из переменных окружения)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# RSS ленты
RSS_URLS = [
    "https://www.coindesk.com/feed/",
    "https://cointelegraph.com/rss",
]

# Настройки
MIN_POSTS_PER_DAY = 5
POST_INTERVAL_HOURS = 2