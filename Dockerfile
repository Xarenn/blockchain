FROM python:3.7

COPY requirements.txt /
RUN pip install -r /requirements.txt

copy . /app
WORKDIR /app

EXPOSE 5000
CMD ["blockchain_http.py"]
