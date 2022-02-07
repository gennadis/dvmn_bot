import os
import time
from pprint import pprint

import requests
from dotenv import load_dotenv

DVMN_REVIEWS_URL = "https://dvmn.org/api/user_reviews/"
DVMN_LONGPOLLING_URL = "https://dvmn.org/api/long_polling/"


def get_reviews(token: str):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(DVMN_REVIEWS_URL, headers=headers)
    response.raise_for_status()

    return response.json()


def get_long_polling(token: str, timestamp: float, timeout: int = 120) -> list[dict]:
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


def main(token: str):
    timestamp = time.time()

    while True:
        try:
            response = get_long_polling(token, timestamp)

        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            print(f"restart cause: {e}")
            continue

        else:
            pprint(response)

            if response["status"] == "timeout":
                timestamp = response["timestamp_to_request"]
            elif response["status"] == "found":
                timestamp = response["last_attempt_timestamp"]


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")
    main(token)
