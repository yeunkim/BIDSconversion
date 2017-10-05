# Use Ubuntu 14.04 LTS
FROM ubuntu:trusty-20170119

## Install python packages
RUN apt-get update && apt-get install -y --no-install-recommends python-pip python-six python-nibabel python-setuptools python-pandas && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN pip install pybids==0.0.1
ENV PYTHONPATH=""

# Install git
RUN apt-get -y update && \
    apt-get -y install git-all

# Install dependencies for dicm2niix
RUN apt-get -y update && apt-get -y install build-essential

RUN apt-get -y update && \
    apt-get -y install pkg-config cmake

# Compile dcm2niix
RUN cd / && git clone https://github.com/yeunkim/dcm2niix.git && \
    cd dcm2niix && mkdir build && cd build && cmake -DBATCH_VERSION=ON .. && make

RUN mkdir /bidsconversion

COPY makeconfigyml.sh /bidsconversion/makeconfigyml.sh
COPY header.txt /bidsconversion/header.txt
COPY bidsconversion /bidsconversion/bidsconversion
COPY bin /bidsconversion/bin

RUN chmod +x /bidsconversion/bin/run.py

COPY json /bidsconversion/json

## To be deprecated
COPY tsv /bidsconversion/tsv

ENTRYPOINT ["/bidsconversion/bin/run.py"]
