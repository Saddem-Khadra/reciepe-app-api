FROM python:3.8.10
MAINTAINER Saddem Khadra

ENV PYTHONUNBUFFERRED 1

COPY ./requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN useradd saddem
USER saddem
