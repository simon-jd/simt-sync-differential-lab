FROM docker.io/library/ubuntu:22.04@sha256:2edbbc5dc405e9612ba3584ce95480277e3eb374407b5505fe26f17df77c7dbc
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ccache git python3 python3-pip python3-yaml python3-pytest wget \
    ca-certificates zlib1g-dev libtinfo5 libtinfo-dev libncurses5 \
    libncurses-dev uuid-dev libboost-serialization-dev libpng-dev \
    libhwloc-dev time && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \
    libtcl8.6 && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
