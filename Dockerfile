FROM python:3.11-alpine3.21

RUN apk update && apk add --no-cache sqlite jq

# Install dependencies
RUN pip install --upgrade pip && pip install beautifulsoup4==4.12.3

COPY ./lotto.py /importer/lotto.py
COPY ./parser.py /importer/parser.py
COPY ./insert_and_update.py /importer/insert_and_update.py
