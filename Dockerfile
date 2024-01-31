FROM python:3.9

# RUN apt update && apt install install binutils 
RUN pip3 install --no-cache --upgrade pip setuptools wheel
COPY requirements.txt /opt/
COPY main.py /opt/
WORKDIR /opt
RUN pip3 install -r requirements.txt
RUN pyinstaller -F main.py -w --clean
