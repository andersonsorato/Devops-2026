FROM python:3.14-slim

WORKDIR /app

COPY app/ ./app/
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.api:APP", "--host", "0.0.0.0", "--port", "8000"]