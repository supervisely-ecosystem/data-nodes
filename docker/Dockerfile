FROM supervisely/base-py-sdk:6.73.137

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y

RUN pip3 install --upgrade setuptools==70.3.0
COPY dev_requirements.txt dev_requirements.txt
RUN pip3 install -r dev_requirements.txt

LABEL python_sdk_version=6.73.383