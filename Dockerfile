FROM python:3.9
ENV PYTHONUNBUFFERED 1

# Prerequisites for python-ldap
RUN apt update && apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev php

# Installer les dépendances système requises pour dlib
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
RUN mkdir /home/lifestylesante

# Specify working directory
WORKDIR /home/lifestylesante

# Copy the requirements file to the working directory
ADD ./requirements.txt /home/lifestylesante

# Install all the python packages inside the requirements file
RUN pip install -r /home/lifestylesante/requirements.txt

# Copy the Django site to the working directory
ADD ./lifestylesante /home/lifestylesante
