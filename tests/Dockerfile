FROM python:3.8-slim

RUN mkdir /app

WORKDIR /app

#host -> container
COPY app.py ./app.py
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["fastapi", "run"]
