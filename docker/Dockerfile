# ============================================================================
# STAGE 1: Builder Stage
# ============================================================================

# todo: remove; temp
# ARG tag_ref_name=6.73.531
ARG tag_ref_name=0.0.1

FROM python:3.10-slim-bookworm AS builder

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1

RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install pip==26.0.1
RUN pip install setuptools==78.1.1 wheel==0.46.2

RUN pip install --upgrade setuptools==70.3.0

RUN pip install --no-cache-dir \
  jsonschema==4.19.2 \
  networkx==3.1 \
  scikit-image==0.21.0 \
  cacheout==0.14.1 \
  markdown==3.5.1 \
  json2html==1.3.0 \
  moviepy==1.0.3 \
  imgaug==0.4.0 \
  imagecorruptions==1.1.2

# todo: remove; temp
# RUN pip install --no-cache-dir supervisely==$tag_ref_name
RUN pip install git+https://github.com/supervisely/supervisely.git@hardened-docker-images

# ============================================================================
# STAGE 2: Runtime Stage (Hardened)
# ============================================================================
FROM supervisely/py-sdk-hardened:${tag_ref_name} AS runtime

# Copy Python environment from builder
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

LABEL python_sdk_version="$tag_ref_name"
