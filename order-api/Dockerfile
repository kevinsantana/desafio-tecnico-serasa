FROM centos/python-38-centos7

USER root

# DEPENDENCIES
RUN yum install -y \
        poppler-utils \
        zlib-devel \
        libpq-devel
RUN pip install --upgrade pip
RUN yum clean all

# INSTALL APPLICATION
COPY ./order_api /deploy/order_api
COPY ./docs /deploy/docs
COPY setup.py /deploy
COPY /tests /deploy/tests
COPY README.md /deploy

WORKDIR /deploy

RUN pip install -e . 

EXPOSE 3090