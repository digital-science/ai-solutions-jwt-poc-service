FROM python:3.13-slim

WORKDIR /usr/src/app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the app
CMD ["python", "server.py"]
