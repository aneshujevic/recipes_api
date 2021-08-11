FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /recipes_api

WORKDIR /recipes_api

ADD . /recipes_api/

RUN pip install -r requirements.txt
