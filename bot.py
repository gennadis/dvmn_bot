import os
import time

import requests
import telegram
from dotenv import load_dotenv

DVMN_REVIEWS_URL = "https://dvmn.org/api/user_reviews/"
DVMN_LONGPOLLING_URL = "https://dvmn.org/api/long_polling/"


def get_response(token: str, timestamp: float, timeout: int = 120) -> list[dict]:
    headers = {"Authorization": f"Token {token}"}
    params = {"timestamp": timestamp}
    response = requests.get(
        url=DVMN_LONGPOLLING_URL,
        headers=headers,
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()

    return response.json()


def compose_notification_text(attempt: dict) -> str:
    lesson_reviewed = f"Преподаватель проверил урок «{attempt['lesson_title']}»."
    lesson_url = f"Ссылка на задачу: {attempt['lesson_url']}"

    if attempt["is_negative"]:
        review_result = "К сожалению, в работе нашлись ошибки! ❌"
    else:
        review_result = (
            "Преподавателю все понравилось, можно приступать к следующему уроку! ✅"
        )

    return f"{lesson_reviewed}\n{review_result}\n{lesson_url}"


def run_long_poll(dvmn_token: str, bot: telegram.Bot, chat_id: int) -> None:
    timestamp = time.time()

    while True:
        try:
            response = get_response(dvmn_token, timestamp)

        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            print(f"Long polling restart cause: {e}")
            time.sleep(5)
            continue

        else:
            if response["status"] == "timeout":
                timestamp = response["timestamp_to_request"]
            elif response["status"] == "found":
                notification_text = compose_notification_text(
                    response["new_attempts"][0]
                )
                bot.send_message(text=notification_text, chat_id=chat_id)
                timestamp = response["last_attempt_timestamp"]


if __name__ == "__main__":
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    user_chat_id = os.getenv("CHAT_ID")

    bot = telegram.Bot(token=telegram_token)
    run_long_poll(dvmn_token=dvmn_token, bot=bot, chat_id=user_chat_id)
