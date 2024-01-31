# FROM python:3.9
FROM python:3.9-alpine

RUN apk add --update  --no-cache binutils  build-base python3-dev libffi-dev py3-cffi
# RUN apt update && apt install install binutils 
RUN pip3 install --no-cache --upgrade pip setuptools wheel
COPY requirements.txt /opt/
COPY main.py /opt/
WORKDIR /opt
RUN pip3 install -r requirements.txt
RUN pyinstaller -F main.py -w --clean
