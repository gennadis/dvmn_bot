import logging
import os
import time

import requests
import telegram

DVMN_LONGPOLLING_URL = "https://dvmn.org/api/long_polling/"


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_token: str, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=tg_token)

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


def run_long_poll(dvmn_token: str, error_timeout: int, logger: logging.Logger) -> None:
    timestamp = time.time()
    logger.info("📗 Telegram bot started.")
    error_message = (
        f"An error has occured. Will try again in {error_timeout} seconds..."
    )

    while True:
        try:
            review = get_code_review(token=dvmn_token, timestamp=timestamp)
        except (
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            requests.RequestException,
        ):
            logger.error(error_message)
            time.sleep(error_timeout)
            continue

        if review["status"] == "timeout":
            timestamp = review["timestamp_to_request"]
        elif review["status"] == "found":
            timestamp = review["last_attempt_timestamp"]
            notification = compose_notification(review["new_attempts"][0])
            logger.info(notification)


if __name__ == "__main__":
    dvmn_token = os.getenv("DVMN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    user_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    error_timeout = os.getenv("ERROR_TIMEOUT")

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Logger")
    logger.addHandler(
        TelegramLogsHandler(tg_token=telegram_token, chat_id=user_chat_id)
    )

    run_long_poll(dvmn_token=dvmn_token, error_timeout=error_timeout, logger=logger)
