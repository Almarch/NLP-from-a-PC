FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

# Install python & jupyter
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY api.py /app/api.py
WORKDIR /app

# Expose port & launch FastAPI
EXPOSE 7777
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7777"]