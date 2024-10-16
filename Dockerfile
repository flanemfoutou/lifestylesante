FROM python:3.9

# Installer les dépendances système requises pour dlib
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./lifestylesante /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT [ "sh", "/entrypoint.sh" ]

