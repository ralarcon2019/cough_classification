FROM python:3.11-slim

# install system deps for audio decoding:
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "cough_classification.wsgi", "--bind", "0.0.0.0:8000"]
