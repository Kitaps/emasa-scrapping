# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update -y
RUN apt-get upgrade -y

RUN pip install --upgrade pip
# RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9001

CMD [ "python", "./main.py"]