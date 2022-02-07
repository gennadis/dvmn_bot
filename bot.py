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


def get_long_polling(token: str):
    headers = {"Authorization": f"Token {token}"}
    # params = {"timestamp": time.time()}
    while True:
        response = requests.get(DVMN_LONGPOLLING_URL, headers=headers)
        response_object = response.json()

        if response_object["status"] == "found":
            pprint(response_object)
            continue
        else:
            pprint(response_object)


def main():
    pass


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")

    # pprint(get_reviews(token))
    get_long_polling(token)
