FROM python:3.11-slim

WORKDIR /app

COPY mock_server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mock_server/ /app/mock_server/

ENV PORT=5000
EXPOSE 5000

WORKDIR /app/mock_server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
