FROM continuumio/miniconda3
LABEL maintainer "Shriniwas <shriniwas26@gmail.com>"

RUN apt update && apt dist-upgrade -y && apt autoremove -y
RUN apt install -y tmux vim htop

WORKDIR /code/

# Install dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Copy data and configs
COPY ./ ./

# Run!
EXPOSE 5005
CMD ["gunicorn", "--bind=0.0.0.0:5005", "covid_dashboard_nl:server"]
