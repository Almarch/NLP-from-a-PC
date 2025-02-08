FROM python:3.10

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY api.py .

# Expose FastAPI port
EXPOSE 80

# Run FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
