FROM nvcr.io/nvidia/deepstream:9.0-triton-multiarch

# Force root for installation and bypass interactive prompts
USER root
ENV DEBIAN_FRONTEND=noninteractive

# Update, install dependencies, run the DeepStream script, and clean up to save space
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    /opt/nvidia/deepstream/deepstream/user_additional_install.sh && \
    pip3 install opencv-python-headless numpy && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
