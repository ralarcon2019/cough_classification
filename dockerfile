FROM python:3.11-slim

# install system deps
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       ffmpeg \
       libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy the rest of your code
COPY . .

# expose port and launch
EXPOSE 8000
CMD ["gunicorn", "cough_classification.wsgi:application", "--bind", "0.0.0.0:8000"]
