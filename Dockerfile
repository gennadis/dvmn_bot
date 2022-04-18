FROM python:3.9-slim-buster

WORKDIR /usr/src/bot
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY bot.py ./

ENTRYPOINT ["python"]
CMD ["bot.py"]
