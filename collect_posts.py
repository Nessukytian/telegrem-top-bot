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
        # время и дата
        time_tag = item.find("time")
        if not time_tag or not time_tag.has_attr("datetime"):
            continue
        dt = datetime.fromisoformat(time_tag["datetime"]).replace(tzinfo=timezone.utc)

        # число реакций
        count = 0
        btn = item.find("button", class_="tgme_widget_message_reactions_button")
        if btn:
            span = btn.find("span", class_="tgme_widget_message_reactions_counter")
            if span and span.text.isdigit():
                count = int(span.text)

        posts.append((dt, count, item))
    return posts

def get_top_posts(channel_username: str):
    """
    Возвращает два bs4.Tag:
      best_any  — самый залайканный (включая пересылы)
      best_orig — самый залайканный оригинал (без метки forwarded)
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    best_any = best_orig = None
    max_any = max_orig = -1

    for dt, cnt, html in parse_messages(channel_username):
        if dt < cutoff:
            continue
        if cnt > max_any:
            best_any, max_any = html, cnt
        if not html.find("a", class_="tgme_widget_message_forwarded") and cnt > max_orig:
            best_orig, max_orig = html, cnt

    return best_any, best_orig
