FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and build frontend
COPY project/package*.json project/
RUN cd project && npm install

COPY project/ project/
RUN cd project && npm run build

# Copy the rest of the application
COPY . .

# Make start script executable
RUN chmod +x start.sh

EXPOSE 8000

CMD ["python", "api_server.py"]