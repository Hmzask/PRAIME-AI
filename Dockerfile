FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

EXPOSE 3000

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0","--port=3000"]