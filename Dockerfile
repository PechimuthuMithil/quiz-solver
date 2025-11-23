# ----- Base Image -----
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_SYSTEM_PYTHON=1

# ----- Install OS dependencies -----
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    && apt-get clean

# ----- Install UV -----
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH
ENV PATH="/root/.local/bin:${PATH}"

# ----- Setup working directory -----
WORKDIR /app

# ----- Copy application -----
COPY . /app

# ----- Create virtual environment -----
RUN uv venv

# Install Python dependencies
RUN uv pip install -r requirements.txt

# ----- Install playwright -----
RUN playwright install-deps
RUN playwright install

# ----- Expose API port -----
EXPOSE 8000

# ----- Start the app -----
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
