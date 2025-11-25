# OCR识别服务

基于FastAPI的OCR识别服务，支持图片和PDF文件的OCR识别。

## 功能特性

- 单张图片OCR识别
- PDF多页OCR识别
- 返回Markdown格式的文本内容

## 安装依赖

```bash
pip install -r requirements.txt
```

注意：使用pdf2image需要安装poppler：
- macOS: `brew install poppler`
- Ubuntu: `sudo apt-get install poppler-utils`
- Windows: 下载poppler并添加到PATH

## 运行服务

```bash
python main.py
```

或者使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问 http://localhost:8000/docs 查看API文档。

## 设备配置（GPU/CPU）

默认情况下，服务会自动检测并使用可用的设备（优先使用GPU）。你也可以通过环境变量 `MINERU_DEVICE_MODE` 来指定设备：

```bash
# 使用CPU
export MINERU_DEVICE_MODE=cpu
python main.py

# 使用GPU（CUDA）
export MINERU_DEVICE_MODE=cuda
python main.py

# 使用指定的GPU（例如第一个GPU）
export MINERU_DEVICE_MODE=cuda:0
python main.py

# macOS上使用Metal Performance Shaders
export MINERU_DEVICE_MODE=mps
python main.py
```

支持的设备类型：
- `cpu`: 使用CPU
- `cuda`: 使用默认GPU（如果可用）
- `cuda:0`, `cuda:1`, ...: 使用指定的GPU
- `mps`: macOS的Metal Performance Shaders
- 不设置：自动检测（优先使用GPU，如果不可用则使用CPU）

## Docker部署

### 构建镜像

```bash
docker build -t ocr-service .
```

### 运行容器

**使用CPU（默认）：**
```bash
docker run -d -p 8000:8000 --name ocr-service ocr-service
```

**使用GPU（需要NVIDIA Docker支持）：**
```bash
docker run -d -p 8000:8000 --gpus all -e MINERU_DEVICE_MODE=cuda --name ocr-service ocr-service
```

**使用指定的GPU：**
```bash
docker run -d -p 8000:8000 --gpus device=0 -e MINERU_DEVICE_MODE=cuda:0 --name ocr-service ocr-service
```

**强制使用CPU（覆盖默认值）：**
```bash
docker run -d -p 8000:8000 -e MINERU_DEVICE_MODE=cpu --name ocr-service ocr-service
```

### 查看日志

```bash
docker logs -f ocr-service
```

### 停止容器

```bash
docker stop ocr-service
docker rm ocr-service
```

## API接口

### 1. 图片OCR识别

**接口地址**: `POST /ocr/image`

**请求**: 上传图片文件（multipart/form-data）

**响应**:
```json
{
    "md_content": "识别出的markdown文本",
    "page": 1
}
```

### 2. PDF OCR识别

**接口地址**: `POST /ocr/pdf`

**请求**: 上传PDF文件（multipart/form-data）

**响应**:
```json
[
    {
        "md_content": "第1页的markdown文本",
        "page": 1
    },
    {
        "md_content": "第2页的markdown文本",
        "page": 2
    }
]
```

## 使用示例

### 使用curl测试图片OCR

```bash
curl -X POST "http://localhost:8000/ocr/image" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

### 使用curl测试PDF OCR

```bash
curl -X POST "http://localhost:8000/ocr/pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf"
```

### 使用Python requests

```python
import requests

# 图片OCR
with open('test_image.jpg', 'rb') as f:
    response = requests.post('http://localhost:8000/ocr/image', files={'file': f})
    print(response.json())

# PDF OCR
with open('test.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/ocr/pdf', files={'file': f})
    print(response.json())
```

