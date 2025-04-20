# Dockerfile

# 1) Start from the official Python 3.11 slim image
FROM python:3.11-slim

# 2) Install OS‑level deps: ffmpeg + libsndfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# 3) Set your working dir
WORKDIR /code

# 4) Copy and install Python deps
COPY requirements.txt .
# tell pip to pull Torch CPU wheels from the PyTorch index as an extra repo:
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r requirements.txt

# 5) Copy the rest of your Django app
COPY . .

# 6) Collect static & migrate (if you need)
RUN python manage.py collectstatic --noinput

# 7) Your CMD (or you can wire this up in App Platform processes)
CMD ["gunicorn", "cough_classification.wsgi:application", "--bind", "0.0.0.0:8000"]
