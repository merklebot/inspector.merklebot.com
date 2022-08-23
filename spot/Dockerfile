FROM ros:melodic-ros-base-bionic

ENV LOGURU_LEVEL INFO
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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
        xvfb \
        libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3.8 -m ensurepip --upgrade

WORKDIR /merklebot_inspector

COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt
COPY . ./

# Install as editable module
RUN python3.8 -m pip install -e .

CMD ["python3.8", "-m", "merklebot_inspector"]
