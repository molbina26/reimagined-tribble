import feedparser
from datetime import datetime
from config import RSS_URLS


def fetch_news():
    """Получение новостей из RSS лент"""
    news_list = []

    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # Берём последние 10 новостей
                news_list.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', url)
                })
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {e}")

    # Сортировка по дате публикации
    news_list.sort(key=lambda x: x['published'], reverse=True)
    return news_list


def get_new_news(last_published=None):
    """Получение только новых новостей"""
    all_news = fetch_news()

    if last_published is None:
        return all_news[:10]  # При первом запуске возвращаем последние 10

    new_news = []
    for news in all_news:
        if news['published'] > last_published:
            new_news.append(news)

    return new_news


if __name__ == "__main__":
    news = fetch_news()
    print(f"Получено {len(news)} новостей")
    for n in news[:3]:
        print(f"- {n['title'][:50]}...")