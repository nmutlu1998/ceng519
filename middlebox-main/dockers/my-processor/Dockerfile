FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential

RUN pip install --upgrade pip && \
    pip install numpy==1.23.5 && \
    pip install scapy nats-py pandas scikit-learn==1.2.2

WORKDIR /code/my-processor
