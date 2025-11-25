# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# poppler-utils: pdf2image需要
# libgl1: PaddleOCR需要
# libglib2.0-0: PaddleOCR需要
# libsm6 libxext6 libxrender-dev: 图像处理需要
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

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

