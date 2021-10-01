FROM python:3.7-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache postgresql-dev libressl-dev build-base alpine-sdk gcc musl-dev python3-dev \
        libffi-dev openssl-dev cargo jpeg-dev zlib-dev

RUN python -m pip install --upgrade pip && pip install --upgrade wheel
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .