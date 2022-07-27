FROM ros:melodic-ros-base-bionic

RUN DEBIAN_FRONTEND=noninteractive apt-get -yqq update && \
    apt-get install -yqq software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get -yqq update && \
    apt-get install -yqq --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        ssh \
        libssl-dev \
        pkg-config \
        python3.8-full \
        python3.8-dev \
        ffmpeg  \
        libsm6 \
        libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3.8 -m ensurepip --upgrade


WORKDIR /code

COPY requirements.txt requirements.txt
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt
COPY . .

CMD ["python3.8", "main.py"]

