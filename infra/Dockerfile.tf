# Optimized Dockerfile to build a TF CPU-enabled image with smaller layers
# Uses multi-stage build pattern to reduce final image size where possible.
FROM python:3.10-slim AS build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN python -m pip install --upgrade pip setuptools wheel

# Install TF CPU wheel and common deps into /opt/venv to reduce final image size
RUN python -m pip install --no-cache-dir -t /opt/py-packages \
    tensorflow-cpu==2.12.0 numpy scipy pandas matplotlib paho-mqtt scikit-learn

# Final image: copy only necessary files and installed packages
FROM python:3.10-slim
COPY --from=build /opt/py-packages /usr/local/lib/python3.10/site-packages
WORKDIR /app
COPY . /app

# Install only small runtime deps if any (none needed since packages copied)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "src.cli"]
