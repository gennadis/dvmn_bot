import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

DVMN_LONGPOLLING_URL = "https://dvmn.org/api/long_polling/"


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_token: str, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=tg_token)
        self.tg_bot.send_message(
            chat_id=self.chat_id, text="📗 Telegram bot started successfully"
        )

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_code_review(token: str, timestamp: float, timeout: int = 120) -> list[dict]:
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


def compose_notification(attempt: dict) -> str:
    lesson_reviewed = f"Преподаватель проверил урок «{attempt['lesson_title']}»."
    lesson_url = f"Ссылка на задачу: {attempt['lesson_url']}"

    if attempt["is_negative"]:
        review_result = "К сожалению, в работе нашлись ошибки! ❌"
    else:
        review_result = (
            "Преподавателю все понравилось, можно приступать к следующему уроку! ✅"
        )

    return f"{lesson_reviewed}\n{review_result}\n{lesson_url}"


def run_long_poll(dvmn_token: str, logger: logging.Logger) -> None:
    logger.info("📗 Dvmn API long polling started successfully")
    timestamp = time.time()

    while True:
        try:
            review = get_code_review(token=dvmn_token, timestamp=timestamp)

        except requests.exceptions.ReadTimeout as timeout_err:
            logger.error(msg=timeout_err, exc_info=True)
            continue

        except requests.exceptions.ConnectionError as connection_err:
            logger.error(msg=connection_err, exc_info=True)
            time.sleep(10)
            continue

        if review["status"] == "timeout":
            timestamp = review["timestamp_to_request"]
        elif review["status"] == "found":
            timestamp = review["last_attempt_timestamp"]
            notification = compose_notification(review["new_attempts"][0])
            logger.info(notification)


if __name__ == "__main__":
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    user_chat_id = os.getenv("TG_CHAT_ID")

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Logger")
    logger.addHandler(
        TelegramLogsHandler(tg_token=telegram_token, chat_id=user_chat_id)
    )

    run_long_poll(dvmn_token=dvmn_token, logger=logger)
