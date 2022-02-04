FROM python:3.10.2-slim-buster

WORKDIR /Athena

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN apt-get update
RUN apt-get install nano
RUN apt-get install iputils-ping
RUN apt-get install net-tools

CMD ["python3", "./main.py"]