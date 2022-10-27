FROM python:3.10.8-slim-bullseye
LABEL maintainer "Shriniwas <shriniwas26@gmail.com>"

RUN apt-get update && apt-get dist-upgrade -y
RUN apt-get install -y vim build-essential

WORKDIR /code/

# Install dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Copy data and configs
# COPY ./ ./

# Run!
EXPOSE 8080
