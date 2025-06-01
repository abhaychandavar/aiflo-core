FROM python:3.12.7-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]