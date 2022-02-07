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


def get_long_polling(token: str, timeout: int):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(DVMN_LONGPOLLING_URL, headers=headers, timeout=timeout)
    response.raise_for_status()

    return response.json()


def main():
    pass


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")

    while True:
        try:
            print(get_long_polling(token, 60))
        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            print(f"restart cause: {e}")
            continue
