# Optimized Dockerfile with labels via build-args
FROM python:3.10-slim AS build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

RUN python -m pip install --no-cache-dir -t /opt/py-packages \
    tensorflow-cpu==2.12.0 numpy scipy pandas matplotlib paho-mqtt scikit-learn

FROM python:3.10-slim
COPY --from=build /opt/py-packages /usr/local/lib/python3.10/site-packages
WORKDIR /app
COPY . /app

# Build args for labels
ARG VCS_URL=""
ARG VERSION=""
ARG DESCRIPTION="CitySafeSense - Edge AI for Urban Safety & Mobility"
ARG TITLE="CitySafeSense"

LABEL org.opencontainers.image.title="${TITLE}"
LABEL org.opencontainers.image.description="${DESCRIPTION}"
LABEL org.opencontainers.image.source="${VCS_URL}"
LABEL org.opencontainers.image.version="${VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "src.cli"]
