FROM python:3.7

COPY requirements.txt /
RUN pip install -r /requirements.txt

copy . /app
WORKDIR /app

CMD ["blockchain_http.py"]
