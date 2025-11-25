#!/usr/bin/env python3
"""
OCR API测试脚本
用于测试图片和PDF的OCR识别接口
"""

import os
import sys
import requests
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试文件路径
DATA_DIR = project_root / "data"
IMAGE_DIR = DATA_DIR / "image"
PDF_DIR = DATA_DIR / "pdf"


def test_image_ocr(image_path: Path):
    """测试图片OCR接口"""
    print(f"\n{'='*60}")
    print(f"测试图片OCR: {image_path.name}")
    print(f"{'='*60}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            response = requests.post(f"{BASE_URL}/ocr/image", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 识别成功")
            print(f"页码: {result.get('page', 'N/A')}")
            print(f"Markdown内容长度: {len(result.get('md_content', ''))} 字符")
            print(f"\nMarkdown内容预览（前500字符）:")
            print("-" * 60)
            md_content = result.get('md_content', '')
            print(md_content[:500] + ("..." if len(md_content) > 500 else ""))
            print("-" * 60)
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_pdf_ocr(pdf_path: Path):
    """测试PDF OCR接口"""
    print(f"\n{'='*60}")
    print(f"测试PDF OCR: {pdf_path.name}")
    print(f"{'='*60}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/ocr/pdf", files=files)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 识别成功")
            print(f"总页数: {len(results)}")
            
            for i, result in enumerate(results, 1):
                page = result.get('page', i)
                md_content = result.get('md_content', '')
                print(f"\n第 {page} 页:")
                print(f"  - Markdown内容长度: {len(md_content)} 字符")
                if md_content:
                    print(f"  - 内容预览（前200字符）:")
                    print(f"    {md_content[:200]}{'...' if len(md_content) > 200 else ''}")
                else:
                    print(f"  - ⚠️  内容为空")
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ 服务运行正常: {response.json()}")
            return True
        else:
            print(f"❌ 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务: {str(e)}")
        print(f"请确保服务已启动在 {BASE_URL}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("OCR API 测试脚本")
    print("=" * 60)
    
    # 检查服务是否运行
    if not test_health_check():
        sys.exit(1)
    
    # 测试图片OCR
    print(f"\n{'='*60}")
    print("开始测试图片OCR接口")
    print(f"{'='*60}")
    
    image_files = sorted(IMAGE_DIR.glob("*.png"))
    if not image_files:
        print(f"⚠️  未找到测试图片文件在 {IMAGE_DIR}")
    else:
        image_success = 0
        for image_file in image_files:
            if test_image_ocr(image_file):
                image_success += 1
        print(f"\n图片OCR测试完成: {image_success}/{len(image_files)} 成功")
    
    # 测试PDF OCR
    print(f"\n{'='*60}")
    print("开始测试PDF OCR接口")
    print(f"{'='*60}")
    
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️  未找到测试PDF文件在 {PDF_DIR}")
    else:
        pdf_success = 0
        for pdf_file in pdf_files:
            if test_pdf_ocr(pdf_file):
                pdf_success += 1
        print(f"\nPDF OCR测试完成: {pdf_success}/{len(pdf_files)} 成功")
    
    print(f"\n{'='*60}")
    print("所有测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

