FROM ubuntu:22.04 AS builder
RUN apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential cmake clang openssl libssl-dev zlib1g-dev gperf wget git ninja-build libsecp256k1-dev libsodium-dev libmicrohttpd-dev liblz4-dev pkg-config autoconf automake libtool libjemalloc-dev lsb-release software-properties-common gnupg

RUN wget https://apt.llvm.org/llvm.sh && \
    chmod +x llvm.sh && \
    ./llvm.sh 16 all && \
    rm -rf /var/lib/apt/lists/*

ENV CC=/usr/bin/clang-16
ENV CXX=/usr/bin/clang++-16
ENV CCACHE_DISABLE=1

WORKDIR /
RUN mkdir ton
WORKDIR /ton

COPY ./ton ./ton

RUN mkdir build && \
        cd build && \
        cmake -GNinja -DNDEBUG=ON -DCMAKE_BUILD_TYPE=Release -DPORTABLE=1 -DTON_ARCH= -DTON_USE_JEMALLOC=ON .. && \
        ninja emulator


FROM python:3.9
COPY --from=builder /ton/emulator/lib/* /usr/local/lib/

COPY requirements.txt /opt/app/
RUN pip3 install -r /opt/app/requirements.txt

COPY model /opt/app/model
COPY parsers /opt/app/parsers
COPY db.py /opt/app/
COPY main.py /opt/app/

ENV EMULATOR_LIBRARY=/usr/local/lib/libemulator.so

WORKDIR /opt/app/
CMD ["python", "main.py"]