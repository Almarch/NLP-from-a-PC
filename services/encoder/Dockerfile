FROM ubuntu:22.04 

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY api.py /app/api.py
WORKDIR /app

EXPOSE 80
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]