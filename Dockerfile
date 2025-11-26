# 使用Python 3.11作为基础镜像
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# 设置时区环境变量，避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
# 让容器默认暴露所有 GPU，并加载驱动工具能力
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
# PyTorch CUDA 源与版本
ARG TORCH_VERSION=2.3.1
ARG TORCHVISION_VERSION=0.18.1
ARG CUDA_PYTORCH_TAG=cu121
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/${CUDA_PYTORCH_TAG}
ENV PIP_NO_CACHE_DIR=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# python3.11 python3.11-venv python3-pip: Python 3.11 和 pip
# poppler-utils: pdf2image需要
# libgl1: PaddleOCR需要
# libglib2.0-0: PaddleOCR需要
# libsm6 libxext6 libxrender-dev: 图像处理需要
RUN apt-get update && apt-get install -y \
    tzdata \
    software-properties-common \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建 Python 3.11 的符号链接和更新 pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && python3 -m pip install --upgrade pip

# 复制requirements文件
COPY requirements.txt .
# 复制 GPU 版本约束，防止依赖里拖回 CPU 版
COPY constraints-cu121.txt .

# 安装Python依赖（包含 GPU 版 torch/torchvision/triton）
RUN pip install --upgrade-strategy only-if-needed --no-cache-dir \
    torch==${TORCH_VERSION}+${CUDA_PYTORCH_TAG} torchvision==${TORCHVISION_VERSION}+${CUDA_PYTORCH_TAG} triton==2.3.1 \
    -c constraints-cu121.txt \
    && pip install --upgrade-strategy only-if-needed --no-cache-dir -r requirements.txt -c constraints-cu121.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV MINERU_MODEL_SOURCE=modelscope
# 设备配置：cpu, cuda, cuda:0 等，默认使用cpu（可在运行时通过 -e MINERU_DEVICE_MODE=cuda 覆盖）
ENV MINERU_DEVICE_MODE=cpu
# 限制线程数，避免 onnxruntime 的 pthread_create 权限问题
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
