FROM python:3-alpine as stage

# Set up requirements
COPY requirements.txt ./requirements.txt
RUN apk add --upgrade --no-cache build-base libffi-dev openssl-dev libgcc
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" VIRTUAL_ENV="/opt/venv"
RUN pip install --no-cache-dir -r requirements.txt

# Main image
FROM python:3-alpine

COPY --from=stage /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" VIRTUAL_ENV="/opt/venv"

ADD run.py /run.py

ENTRYPOINT [ "python3", "/run.py" ]
