cp ../dev_requirements.txt . && \
docker build --no-cache -t supervisely/data-nodes:sdk-test . && \
rm dev_requirements.txt
docker push supervisely/data-nodes:sdk-test