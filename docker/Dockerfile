FROM supervisely/base-py-sdk:6.73.486

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y

RUN pip3 install --upgrade setuptools==70.3.0

RUN pip3 install --no-cache-dir jsonschema==4.19.2 \
    networkx==3.1 \
    scikit-image==0.21.0 \
    cacheout==0.14.1 \
    markdown==3.5.1 \
    json2html==1.3.0 \
    moviepy==1.0.3 \
    imgaug==0.4.0 \
    imagecorruptions==1.1.2

RUN pip3 install --no-cache-dir supervisely==6.73.486

LABEL python_sdk_version=6.73.486