FROM python:3.11-slim

# Per PyTorch servono spesso alcune lib di sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]