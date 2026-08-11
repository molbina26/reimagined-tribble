require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const Parser = require('rss-parser');
const axios = require('axios');

const BOT_TOKEN = process.env.BOT_TOKEN;
const CHANNEL_ID = process.env.CHANNEL_ID;

const RSS_URLS = [
    'https://www.coindesk.com/feed/',
    'https://cointelegraph.com/rss',
];

const parser = new Parser();
let lastPublishedLink = null;

// Инициализация бота
const bot = new TelegramBot(BOT_TOKEN, { polling: false });

// Функция перевода через Google Translate
async function translateToRussian(text) {
    if (!text) return '';
    try {
        // Очистка от HTML
        text = text.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ');

        const encodedText = encodeURIComponent(text);
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ru&dt=t&q=${encodedText}`;

        const response = await axios.get(url);
        if (response.data && response.data[0]) {
            return response.data[0].map(item => item[0]).join('');
        }
        return text;
    } catch (e) {
        console.error('Ошибка перевода:', e.message);
        return text;
    }
}

// Получение новостей из RSS
async function fetchNews() {
    const allNews = [];

    for (const url of RSS_URLS) {
        try {
            const feed = await parser.parseURL(url);
            for (const entry of feed.items.slice(0, 10)) {
                allNews.push({
                    title: entry.title,
                    link: entry.link,
                    summary: entry.contentSnippet || entry.summary || '',
                    published: entry.pubDate || entry.isoDate,
                    source: feed.title
                });
            }
        } catch (e) {
            console.error(`Ошибка парсинга ${url}:`, e.message);
        }
    }

    // Сортировка по дате
    allNews.sort((a, b) => new Date(b.published) - new Date(a.published));
    return allNews;
}

// Форматирование поста
function formatPost(news) {
    let summary = news.summary.replace(/<[^>]*>/g, '').trim();
    if (summary.length > 300) {
        summary = summary.substring(0, 300) + '...';
    }

    return `📰 <b>${news.title}</b>\n\n${summary}\n\n<a href="${news.link}">Читать далее</a>\n\nИсточник: ${news.source}`;
}

// Публикация новости
async function postNews() {
    console.log('Проверка новостей...');

    const newsList = await fetchNews();

    for (const news of newsList.slice(0, 3)) {
        if (news.link === lastPublishedLink) continue;

        try {
            const translatedTitle = await translateToRussian(news.title);
            const translatedSummary = await translateToRussian(news.summary);

            const postText = `📰 <b>${translatedTitle}</b>\n\n${translatedSummary.substring(0, 300)}...\n\n<a href="${news.link}">Читать далее</a>\n\nИсточник: ${news.source}`;

            await bot.sendMessage(CHANNEL_ID, postText, { parse_mode: 'HTML' });

            lastPublishedLink = news.link;
            console.log(`Опубликовано: ${translatedTitle.substring(0, 30)}...`);

            await new Promise(r => setTimeout(r, 60000));
        } catch (e) {
            console.error('Ошибка публикации:', e.message);
        }
    }
}

// Запуск
async function main() {
    console.log('Бот запущен!');

    // Отправка сообщения о запуске
    try {
        await bot.sendMessage(CHANNEL_ID, '🤖 Бот крипто-новостей активирован!\nТеперь я буду публиковать новости из RSS лент.');
    } catch (e) {
        console.error('Не удалось отправить сообщение:', e.message);
    }

    // Проверка новостей каждые 30 минут
    setInterval(async () => {
        const hour = new Date().getHours();
        if (hour >= 8 && hour <= 23) {
            await postNews();
        }
    }, 30 * 60 * 1000);
}

main();