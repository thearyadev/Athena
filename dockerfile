FROM python:3.10.2-slim-buster

COPY ./data ./data
COPY ./utils ./utils
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD ["python3", "./main.py"]