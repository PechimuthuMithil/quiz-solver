# ------------------------------
# Base Image (Python 3.11)
# ------------------------------
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_SYSTEM_PYTHON=1

# ------------------------------
# System Dependencies
# ------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxshmfence1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Install uv
# ------------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# ------------------------------
# Working Directory
# ------------------------------
WORKDIR /app
COPY . /app

# ------------------------------
# Python Dependencies
# ------------------------------
RUN uv venv
RUN uv pip install --no-cache-dir -r requirements.txt

# ------------------------------
# Playwright Install
# ------------------------------
RUN playwright install-deps
RUN playwright install

# ------------------------------
# Expose API Port
# ------------------------------
EXPOSE 8000

# ------------------------------
# Start FastAPI App
# ------------------------------
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
