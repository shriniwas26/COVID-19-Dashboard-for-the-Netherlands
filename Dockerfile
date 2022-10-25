FROM python:3.10.8-slim-bullseye
LABEL maintainer "Shriniwas <shriniwas26@gmail.com>"

RUN apt update && apt dist-upgrade -y
RUN apt install -y vim build-essential

WORKDIR /code/

# Install dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Copy data and configs
COPY ./ ./

# Run!
EXPOSE 8080
