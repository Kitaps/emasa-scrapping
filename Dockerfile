# syntax=docker/dockerfile:1

FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache --update \
    python3-dev gcc \
    gfortran musl-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9001

CMD [ "python", "./main.py"]