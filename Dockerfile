FROM python:3.9-slim-bullseye AS BASE

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y \
        cmake \
        build-essential \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl && \
        rm -rf /var/lib/apt/lists/* \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y \
      gcc \
      pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000