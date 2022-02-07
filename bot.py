import os
from pprint import pprint

import requests
from dotenv import load_dotenv

DVMN_REVIEWS_URL = "https://dvmn.org/api/user_reviews/"


def get_reviews(token: str):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(DVMN_REVIEWS_URL, headers=headers)
    response.raise_for_status()

    return response.json()


def main():
    pass


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")

    pprint(get_reviews(token))