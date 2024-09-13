FROM python:3.10

RUN mkdir /fast_app

WORKDIR /fast_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .



CMD gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000