FROM continuumio/miniconda3
LABEL maintainer "Shriniwas <shriniwas26@gmail.com>"

RUN apt update && apt dist-upgrade -y && apt autoremove -y
RUN apt install -y tmux vim htop

WORKDIR /code/

# Create a conda environment for the app
RUN conda create -n dash_env python=3.10
RUN echo "source activate dash_env" > ~/.bashrc
ENV PATH /opt/conda/envs/dash_env/bin:$PATH

# Install dependencies
COPY ./requirements.txt ./
RUN conda install -n dash_env -c conda-forge --file requirements.txt -y

# Copy data and configs
COPY ./ ./

# Run!
EXPOSE 5005
CMD ["/opt/conda/envs/dash_env/bin/gunicorn", "--bind=0.0.0.0:5005", "covid-dashboard-nl:server"]
