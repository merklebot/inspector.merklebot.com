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
        python3.8 \
        ffmpeg  \
        libsm6 \
        xvfb \
        freeglut3 \
        freeglut3-dev \
        libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



WORKDIR /merklebot_inspector


RUN add-apt-repository universe
RUN apt-get update
RUN apt-get -y install python3-pip
COPY requirements.txt ./
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt
COPY . ./

# Install as editable module
RUN python3.8 -m pip install -e .

CMD ["python3.8", "-m", "merklebot_inspector"]
