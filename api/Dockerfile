FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install python-dotenv

EXPOSE 4011

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4011"]
