FROM python:3.9-alpine

WORKDIR /review-bot
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY bot.py ./

ENTRYPOINT ["python"]
CMD ["bot.py"]
