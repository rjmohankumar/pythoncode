FROM python:alpine3.6
LABEL maintainer "cloudops network"

WORKDIR /dockerstool

# copy requirements seperate to make sure we don't compile the modules all the time
COPY requirements.txt ./
RUN apk --no-cache add build-base libffi-dev openssl openssl-dev tzdata \
    && pip install --cache-dir /pipcache --upgrade pip \
    && pip install --cache-dir /pipcache -r requirements.txt \
    && apk del build-base libffi-dev openssl-dev \
    && rm -rf /pipcache /root/.cache/pip
COPY . .

ENTRYPOINT [ "python", "./rt53.py"]
