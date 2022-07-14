FROM python:3.8-alpine
MAINTAINER Saddem Khadra

ENV PYTHONUNBUFFERRED 1

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN python -m pip install --upgrade pip
RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D saddem

RUN chown -R saddem:saddem /vol/
RUN chmod -R 755 /vol/web

USER saddem
