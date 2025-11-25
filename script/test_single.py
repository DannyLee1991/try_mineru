#!/usr/bin/env python3
"""
单个文件OCR测试脚本
用法: python script/test_single.py <文件路径> [--type image|pdf]
"""

import os
import sys
import requests
import json
import argparse
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000"


def test_image_ocr(image_path: Path, base_url: str = BASE_URL):
    """测试单张图片OCR"""
    print(f"测试图片OCR: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        response = requests.post(f"{base_url}/ocr/image", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 识别成功")
        print(f"页码: {result.get('page', 'N/A')}")
        print(f"\nMarkdown内容:")
        print("=" * 60)
        print(result.get('md_content', ''))
        print("=" * 60)
        
        # 保存结果到文件
        output_file = image_path.parent / f"{image_path.stem}_ocr_result.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.get('md_content', ''))
        print(f"\n结果已保存到: {output_file}")
        return True
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return False


def test_pdf_ocr(pdf_path: Path, base_url: str = BASE_URL):
    """测试PDF OCR"""
    print(f"测试PDF OCR: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path.name, f, 'application/pdf')}
        response = requests.post(f"{base_url}/ocr/pdf", files=files)
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n✅ 识别成功")
        print(f"总页数: {len(results)}")
        
        # 保存结果到文件
        output_file = pdf_path.parent / f"{pdf_path.stem}_ocr_result.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                page = result.get('page', 0)
                md_content = result.get('md_content', '')
                f.write(f"\n{'='*60}\n")
                f.write(f"第 {page} 页\n")
                f.write(f"{'='*60}\n\n")
                f.write(md_content)
                f.write("\n\n")
        
        print(f"\n结果已保存到: {output_file}")
        
        # 显示每页摘要
        for result in results:
            page = result.get('page', 0)
            md_content = result.get('md_content', '')
            print(f"\n第 {page} 页: {len(md_content)} 字符")
            if md_content:
                print(f"  预览: {md_content[:100]}...")
        
        return True
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return False


def main():
    parser = argparse.ArgumentParser(description='测试OCR API接口')
    parser.add_argument('file', type=str, help='要测试的文件路径')
    parser.add_argument('--type', choices=['image', 'pdf'], help='文件类型（可选，自动检测）')
    parser.add_argument('--url', type=str, default=BASE_URL, help=f'API服务URL（默认: {BASE_URL}）')
    
    args = parser.parse_args()
    
    base_url = args.url
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    # 自动检测文件类型
    if args.type:
        file_type = args.type
    else:
        ext = file_path.suffix.lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            file_type = 'image'
        elif ext == '.pdf':
            file_type = 'pdf'
        else:
            print(f"❌ 不支持的文件类型: {ext}")
            sys.exit(1)
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ 服务异常: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务: {str(e)}")
        print(f"请确保服务已启动在 {base_url}")
        sys.exit(1)
    
    # 执行测试
    if file_type == 'image':
        success = test_image_ocr(file_path, base_url)
    else:
        success = test_pdf_ocr(file_path, base_url)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

