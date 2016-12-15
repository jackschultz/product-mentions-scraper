FROM ubuntu:14.04

MAINTAINER Jack Schultz "jackschultz23@gmail.com"

# get up to date
RUN \
  apt-get -qq update && \
  apt-get upgrade -y  && \
  apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    python-dev \
    python-virtualenv \
    libpq-dev \
    python-psycopg2 \
    libxml2-dev \
    libxslt-dev \
    libncurses5-dev \
    libffi-dev \
    vim && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /product_mentions_scraper

COPY . /product_mentions_scraper

# create a virtualenv we can later use
RUN mkdir -p /venv/
RUN virtualenv /venv/

# install python dependencies from pypi into venv
RUN /venv/bin/pip install -r /product_mentions_scraper/requirements.txt

ENV PORT 5000
ENV PMS_DATABASE_URI postgresql://postgres:password@postgres:5432/product_mentions_development

# expose a port for the flask development server
EXPOSE 5000

# run our flask app inside the container
CMD /venv/bin/python app.py
