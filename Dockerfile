FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --upgrade pip

# Install PyTorch with CUDA support
RUN pip3 install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
RUN pip3 install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    opencv-python==4.8.1.78 \
    pillow==10.1.0 \
    numpy==1.24.3 \
    scipy==1.11.4 \
    matplotlib==3.7.3 \
    imageio==2.31.6 \
    imageio-ffmpeg==0.4.9 \
    librosa==0.10.1 \
    numba==0.58.1 \
    resampy==0.4.2 \
    pydub==0.25.1 \
    face-alignment==1.3.5 \
    scikit-image==0.21.0 \
    dlib==19.24.2 \
    yacs==0.1.8 \
    pyyaml==6.0.1 \
    joblib==1.3.2 \
    tqdm==4.66.1 \
    gfpgan==1.3.8 \
    basicsr==1.4.2

# Create app directory
WORKDIR /app

# Copy application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]