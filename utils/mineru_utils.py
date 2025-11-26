import os
from typing import Optional
from mineru.cli.common import read_fn, do_parse


def configure_pytorch_safe_loading():
    """
    配置 PyTorch 的安全加载机制，允许加载 doclayout_yolo 模型。
    这是 PyTorch 2.6 的安全更新所需的配置。
    
    由于 doclayout_yolo 库中的 torch.load 调用没有指定 weights_only 参数，
    我们需要通过以下方式解决：
    1. 添加安全全局变量以允许加载 YOLOv10DetectionModel
    2. 如果可能，monkey patch torch.load 以提供默认的 weights_only=False
    """
    try:
        import torch
        from torch import serialization
        
        # 方法1: 添加安全全局变量
        try:
            from doclayout_yolo.nn.tasks import YOLOv10DetectionModel
            # 添加安全全局变量，允许加载包含此类的模型
            serialization.add_safe_globals([YOLOv10DetectionModel])
        except ImportError:
            # 如果导入失败，跳过
            pass
        
        # 方法2: Monkey patch torch.load 以提供向后兼容性
        # 保存原始的 torch.load
        if not hasattr(torch, '_original_load'):
            torch._original_load = torch.load
            
            def patched_load(*args, **kwargs):
                # 如果没有指定 weights_only，默认设置为 False（向后兼容）
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return torch._original_load(*args, **kwargs)
            
            torch.load = patched_load
            
    except ImportError:
        # 如果没有安装 torch，跳过配置
        pass


def parse_doc_to_md(file_path: str, output_dir: str, device: Optional[str] = None):
    """
    解析PDF文档为markdown（同步版本）
    
    参数:
        file_path: PDF文件路径
        output_dir: 输出目录
        device: 设备类型，可选值：
            - 'cpu': 使用CPU
            - 'cuda': 使用GPU（默认）
            - 'cuda:0': 使用第一个GPU
            - 'mps': macOS的Metal Performance Shaders
            - None: 从环境变量 MINERU_DEVICE_MODE 读取，如果未设置则自动检测
    """
    # 配置 PyTorch 安全加载（必须在加载模型前调用）
    configure_pytorch_safe_loading()
    
    # 设置设备模式
    if device is None:
        # 从环境变量读取，如果未设置则自动检测
        device = os.getenv('MINERU_DEVICE_MODE')
        if device is None:
            # 自动检测：如果有CUDA则使用cuda，否则使用cpu
            try:
                import torch
                if torch.cuda.is_available():
                    device = 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    device = 'mps'
                else:
                    device = 'cpu'
            except ImportError:
                device = 'cpu'
    
    # 验证设备是否可用，如果不可用则回退到 CPU
    if device and device.startswith('cuda'):
        try:
            import torch
            if not torch.cuda.is_available():
                print(f"警告: 配置的设备 {device} 不可用（未检测到 NVIDIA GPU），回退到 CPU")
                device = 'cpu'
        except (ImportError, Exception) as e:
            print(f"警告: 无法验证 CUDA 设备，回退到 CPU: {e}")
            device = 'cpu'
    
    # 设置环境变量，供mineru使用
    original_device_mode = os.getenv('MINERU_DEVICE_MODE')
    os.environ['MINERU_DEVICE_MODE'] = device
    print(f"使用设备: {device}")
    
    try:
        # 处理文件哈希列表
        pdf_bytes_list = []
        
        pdf_bytes = read_fn(
            str(file_path)
        )
        pdf_bytes_list.append(pdf_bytes)

        print(f"start parse pdf to md")

        # 调用同步处理函数
        do_parse(
            output_dir=output_dir,
            pdf_file_names=["parsed"],
            pdf_bytes_list=pdf_bytes_list,
            p_lang_list=['ch'],
            f_draw_layout_bbox=False,
            f_draw_span_bbox=False,
            f_dump_md=True,
            f_dump_middle_json=False,
            f_dump_model_output=False,
            f_dump_orig_pdf=False,
            f_dump_content_list=False,
        )
        print(f"end parse pdf to md")

    except Exception as e:
        print(f"PDF解析错误: {e}")
        raise e
    finally:
        # 恢复原始环境变量
        if original_device_mode is not None:
            os.environ['MINERU_DEVICE_MODE'] = original_device_mode
        elif 'MINERU_DEVICE_MODE' in os.environ:
            del os.environ['MINERU_DEVICE_MODE']

    with open(os.path.join(output_dir, "parsed", "auto", "parsed.md"), "r", encoding="utf-8") as f:
        return f.read()