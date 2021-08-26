FROM centos/python-38-centos7

USER root

# ENVS
ENV SECRET_KEY=$SECRET_KEY

# DEPENDENCIES
RUN yum install -y \
        postgresql-devel\
        poppler-utils \
        zlib-devel \
        libpq-devel
RUN pip install --upgrade pip
RUN yum clean all

# INSTALL APPLICATION
COPY ./user_api /deploy/user_api
COPY ./docs /deploy/docs
COPY setup.py /deploy
COPY /tests /deploy/tests
COPY README.md /deploy

WORKDIR /deploy

RUN pip install -e . 

EXPOSE 7000