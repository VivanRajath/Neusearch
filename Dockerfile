# Stage 1: Build the React Frontend
FROM node:18-alpine AS build
WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code
COPY frontend/ ./
# Build the React application
RUN npm run build

# Stage 2: Setup the Python Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy built frontend assets from the build stage
# We place them in a 'static' directory which FastAPI will serve
COPY --from=build /app/frontend/build /app/static

# Expose port
EXPOSE 8000

# Run the application
# We use the same command as the backend, but the code will be updated to serve static files
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
