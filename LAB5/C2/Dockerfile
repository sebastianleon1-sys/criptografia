FROM ubuntu:18.10

RUN sed -i 's|http://archive.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y openssh-client iproute2 iputils-ping net-tools tcpdump && \
    rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
