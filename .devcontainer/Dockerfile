FROM mcr.microsoft.com/devcontainers/python:3.13

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libturbojpeg0 \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*
