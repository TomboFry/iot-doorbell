FROM python:2.7-alpine
MAINTAINER Tom Gardiner <tom@tombofry.co.uk>

RUN apk add --no-cache git gcc musl-dev libffi-dev openssl-dev && \
    git clone https://github.com/TomboFry/iot-doorbell.git -b develop /doorbell && \
    cd /doorbell && \
    pip install --no-cache-dir -r pip-install.txt && \
    apk del --no-cache git gcc

WORKDIR /doorbell

CMD [ "python", "src/server.py" ]

