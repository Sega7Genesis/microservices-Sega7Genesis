FROM python:3.8.2

WORKDIR /opt/warehouse

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libsasl2-dev \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

# set python env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+x entrypoint.sh

CMD /opt/warehouse/entrypoint.sh
