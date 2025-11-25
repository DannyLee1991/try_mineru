from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import io
import os
import tempfile
import shutil
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from utils.mineru_utils import parse_doc_to_md
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OCR识别服务", description="提供图片和PDF的OCR识别功能")

# 从环境变量读取设备配置，如果没有设置则使用None（自动检测）
DEVICE = os.getenv('MINERU_DEVICE_MODE', None)

@app.get("/")
async def root():
    return {"message": "OCR识别服务已启动"}

@app.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...)):
    """
    对单张图片进行OCR识别
    
    参数:
        file: 上传的图片文件
    
    返回:
        {
            "md_content": "识别出的markdown文本",
            "page": 1
        }
    """
    temp_dir = None
    temp_pdf_path = None
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图片格式")
        
        # 读取文件内容
        contents = await file.read()
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 将图片转换为PDF
        image = Image.open(io.BytesIO(contents))
        # 如果是RGBA模式，转换为RGB
        if image.mode == 'RGBA':
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image
        
        temp_pdf_path = os.path.join(temp_dir, "image.pdf")
        # 使用reportlab将图片转换为PDF
        img_width, img_height = image.size
        # 使用A4页面大小，保持图片宽高比
        page_width, page_height = A4
        scale = min(page_width / img_width, page_height / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2
        
        c = canvas.Canvas(temp_pdf_path, pagesize=A4)
        img_reader = ImageReader(image)
        c.drawImage(img_reader, x, y, width=scaled_width, height=scaled_height)
        c.save()
        
        # 使用mineru进行OCR识别
        md_content = parse_doc_to_md(temp_pdf_path, temp_dir, device=DEVICE)
        
        return {
            "md_content": md_content.strip(),
            "page": 1
        }
    
    except Exception as e:
        logger.error(f"图片OCR识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...)):
    """
    对PDF文件进行OCR识别
    
    参数:
        file: 上传的PDF文件
    
    返回:
        [
            {
                "md_content": "第1页的markdown文本",
                "page": 1
            },
            {
                "md_content": "第2页的markdown文本",
                "page": 2
            },
            ...
        ]
    """
    temp_dir = None
    try:
        # 验证文件类型
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="文件必须是PDF格式")
        
        # 读取文件内容
        contents = await file.read()
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 保存PDF到临时文件
        temp_pdf_path = os.path.join(temp_dir, "input.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(contents)
        
        # 读取PDF获取页数
        pdf_reader = PdfReader(io.BytesIO(contents))
        total_pages = len(pdf_reader.pages)
        
        # 对每一页进行OCR识别
        results = []
        for page_num in range(1, total_pages + 1):
            # 创建单页PDF
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])
            
            page_pdf_path = os.path.join(temp_dir, f"page_{page_num}.pdf")
            with open(page_pdf_path, "wb") as f:
                pdf_writer.write(f)
            
            # 为每页创建独立的输出目录
            page_output_dir = os.path.join(temp_dir, f"output_page_{page_num}")
            os.makedirs(page_output_dir, exist_ok=True)
            
            # 使用mineru进行OCR识别
            try:
                md_content = parse_doc_to_md(page_pdf_path, page_output_dir, device=DEVICE)
                results.append({
                    "md_content": md_content.strip(),
                    "page": page_num
                })
            except Exception as e:
                logger.warning(f"第{page_num}页OCR识别失败: {str(e)}")
                results.append({
                    "md_content": "",
                    "page": page_num
                })
        
        return results
    
    except Exception as e:
        logger.error(f"PDF OCR识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

