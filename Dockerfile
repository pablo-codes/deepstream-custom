FROM nvcr.io/nvidia/deepstream:9.0-samples-multiarch

USER root
ENV DEBIAN_FRONTEND=noninteractive

# 1. Update package lists
# 2. Run the required DeepStream codecs script
# 3. Install Python deps for PyServiceMaker frame extraction pipeline
#
# NOTE: pip installs are split so a failure in the large torch download
# does not silently prevent lightweight deps from being installed.
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    /opt/nvidia/deepstream/deepstream/user_additional_install.sh && \
    pip3 install /opt/nvidia/deepstream/deepstream/service-maker/python/pyservicemaker*.whl opencv-python-headless numpy torch PyYAML --break-system-packages && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
