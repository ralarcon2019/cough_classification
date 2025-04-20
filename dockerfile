# Dockerfile
FROM python:3.11-slim

# install the system packages we need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# create/app directory
WORKDIR /code

# install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# copy the rest of the code
COPY . .

# expose port if you’re using gunicorn
EXPOSE 8000

# your normal run command
CMD ["gunicorn", "cough_classification.wsgi:application", "--bind", "0.0.0.0:8000"]
