FROM python:3.10

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install models
RUN python -m spacy download en_core_web_trf && \
    python -m spacy download fr_dep_news_trf && \
    python -m spacy download es_dep_news_trf

# Copy the application code
COPY api.py .

# Expose FastAPI port
EXPOSE 80

# Run FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
