# collect_posts.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"
}

def parse_messages(channel_username: str):
    url = f"https://t.me/s/{channel_username}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.find_all("div", class_="tgme_widget_message_wrap")
    posts = []

    for item in items:
        # Дата
        time_tag = item.find("time")
        if not time_tag or not time_tag.has_attr("datetime"):
            continue
        dt = datetime.fromisoformat(time_tag["datetime"])
        # Считаем реакции (всегда один <button> на всё сообщение)
        btn = item.find("button", class_="tgme_widget_message_reactions_button")
        count = 0
        if btn:
            # внутри кнопки есть span с числом
            span = btn.find("span", class_="tgme_widget_message_reactions_counter")
            if span and span.text.isdigit():
                count = int(span.text)
        posts.append((dt, count, item))
    return posts

def get_top_posts(channel_username: str):
    """
    Возвращает два сообщения (best_any, best_orig) за последние 24 часа.
    best_any — любое (включая пересылы),
    best_orig — только собственные (когда нет пересылки в HTML нет “forward” метки).
    Для простоты: считаем, что если в html нет <a class="tgme_widget_message_forwarded"> — это оригинал.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    posts = parse_messages(channel_username)
    best_any = best_orig = None
    max_any = max_orig = -1

    for dt, cnt, html in posts:
        if dt.replace(tzinfo=timezone.utc) < cutoff:
            continue
        # общий топ
        if cnt > max_any:
            max_any, best_any = cnt, html
        # топ оригинальных
        if not html.find("a", class_="tgme_widget_message_forwarded") and cnt > max_orig:
            max_orig, best_orig = cnt, html

    return best_any, best_orig
