# OCR API 测试脚本

本目录包含用于测试OCR API接口的脚本。

## 脚本说明

### 1. test_ocr.py
批量测试脚本，自动测试 `data` 目录下的所有图片和PDF文件。

**使用方法：**
```bash
# 确保服务已启动
python script/test_ocr.py
```

**功能：**
- 自动检测服务是否运行
- 测试所有图片文件（data/image/*.png）
- 测试所有PDF文件（data/pdf/*.pdf）
- 显示识别结果摘要

### 2. test_single.py
单个文件测试脚本，用于测试指定的单个文件。

**使用方法：**
```bash
# 测试单个图片
python script/test_single.py data/image/001.png

# 测试单个PDF
python script/test_single.py data/pdf/22023811.pdf

# 指定文件类型
python script/test_single.py data/image/001.png --type image

# 指定API服务URL
python script/test_single.py data/image/001.png --url http://localhost:8000
```

**功能：**
- 测试单个文件
- 自动检测文件类型
- 将识别结果保存到同目录下的 `*_ocr_result.md` 文件
- 显示详细的识别结果

## 依赖要求

```bash
pip install requests
```

## 注意事项

1. 运行测试前，确保OCR服务已启动：
   ```bash
   python main.py
   # 或
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. 默认API地址为 `http://localhost:8000`，如果服务运行在其他地址，请使用 `--url` 参数指定。

3. 测试结果会显示在控制台，`test_single.py` 还会将结果保存到文件。

