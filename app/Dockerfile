FROM python:3.10-slim

WORKDIR /app
COPY . .

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "main.py"]

# Keep container running for development and logging
CMD ["tail", "-f", "/dev/null"]
