FROM centos/python-38-centos7

USER root

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

WORKDIR /deploy

RUN pip install -e . 

# BUILD SPHINX DOCS
RUN /bin/bash -cx 'cd docs; make clean; make html'

CMD bash -c "cd user_api && gunicorn --workers=1 --worker-class=uvicorn.workers.UvicornWorker --timeout=174000 --reload --bind=0.0.0.0:7000 'app:start_application()'"
EXPOSE 7000