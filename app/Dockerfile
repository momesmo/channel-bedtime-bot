FROM python:3.12.7

RUN apt-get update; apt-get install -y --no-install-recommends

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3",  "main.py" ]