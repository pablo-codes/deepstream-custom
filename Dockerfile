FROM nvcr.io/nvidia/deepstream:9.0-triton-multiarch

# Force root for installation and bypass interactive prompts
USER root
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install all required compilers and dependencies for pyds
# 2. Run the DeepStream additional codecs script
# 3. Build the Python bindings (pyds) natively from source using the -b flag
# 4. Install standard Python dependencies and clean up
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev python3-gi python3-gst-1.0 \
    libgirepository1.0-dev gobject-introspection gir1.2-gst-rtsp-server-1.0 \
    python-gi-dev git meson cmake g++ build-essential libglib2.0-dev \
    libgstreamer1.0-dev libtool m4 autoconf automake libcairo2-dev && \
    /opt/nvidia/deepstream/deepstream/user_additional_install.sh && \
    cd /opt/nvidia/deepstream/deepstream && \
    bash user_deepstream_python_apps_install.sh -b && \
    pip3 install opencv-python-headless numpy && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
