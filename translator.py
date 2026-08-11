from deep_translator import GoogleTranslator
import html


def translate_to_russian(text):
    """Перевод текста на русский через Google Translate"""
    if not text:
        return ""

    try:
        # Убираем HTML теги
        clean_text = html.unescape(text)
        # Ограничиваем длину (Google Translate имеет лимит)
        max_len = 4500
        if len(clean_text) > max_len:
            clean_text = clean_text[:max_len] + "..."

        translator = GoogleTranslator(source='auto', target='ru')
        result = translator.translate(clean_text)
        return result if result else text
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


def translate_news(news_item):
    """Перевод новости на русский"""
    translated = {
        'title': translate_to_russian(news_item['title']),
        'summary': translate_to_russian(news_item['summary']),
        'link': news_item['link'],
        'source': news_item['source'],
        'published': news_item['published']
    }
    return translated


if __name__ == "__main__":
    # Тест
    test_text = "Bitcoin reaches new all-time high"
    result = translate_to_russian(test_text)
    print(f"Original: {test_text}")
    print(f"Translated: {result}")