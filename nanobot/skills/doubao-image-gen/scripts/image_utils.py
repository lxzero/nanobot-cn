#!/usr/bin/env python3
"""
图片生成工具 - 共享工具函数
提供尺寸验证、图片下载等通用功能
"""

import os
import re
import urllib.request
import urllib.error
from datetime import datetime


# output/ 目录位于 skill 根目录下（scripts/ 的上级）
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output")


def generate_output_path(prefix="image"):
    """
    在 skill 根目录的 output/ 下生成带时间戳的文件路径，自动创建目录。
    
    Returns:
        str: 如 /path/to/doubao-image-gen/output/image_20260302_233626.jpg
    """
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(DEFAULT_OUTPUT_DIR, f"{prefix}_{ts}.jpg")


def validate_size(size_str, min_pixels=None, max_pixels=None, min_ratio=None, max_ratio=None):
    """
    验证尺寸参数是否符合API要求
    
    Args:
        size_str: 尺寸字符串 (如 "2K", "4K", "3750x1250")
        min_pixels: 最小像素数 (默认 3686400)
        max_pixels: 最大像素数 (默认 16777216)
        min_ratio: 最小宽高比 (默认 1/16)
        max_ratio: 最大宽高比 (默认 16)
        
    Returns:
        tuple: (is_valid, error_message, size_info_dict)
    """
    # 设置默认值
    MIN_PIXELS = min_pixels or 3686400  # 2560x1440
    MAX_PIXELS = max_pixels or 16777216  # 4096x4096
    MIN_RATIO = min_ratio or 1/16
    MAX_RATIO = max_ratio or 16
    
    if not size_str:
        return False, "Size parameter cannot be empty", None
    
    size_str = size_str.strip()
    
    # 检查预设分辨率
    preset_sizes = ['2K', '4K']
    if size_str.upper() in preset_sizes:
        return True, None, {
            'type': 'preset',
            'value': size_str.upper(),
            'description': 'High resolution' if size_str.upper() == '2K' else 'Ultra high resolution'
        }
    
    # 检查自定义宽高格式 (如 3750x1250)
    pattern = r'^(\d+)[xX](\d+)$'
    match = re.match(pattern, size_str)
    
    if not match:
        return False, f"Invalid size format: '{size_str}'. Use '2K', '4K', or 'WIDTHxHEIGHT' (e.g., '3750x1250')", None
    
    width = int(match.group(1))
    height = int(match.group(2))
    
    # 验证像素值范围
    if width <= 0 or height <= 0:
        return False, f"Width and height must be positive integers", None
    
    total_pixels = width * height
    
    if total_pixels < MIN_PIXELS:
        return False, (
            f"Total pixels {total_pixels} ({width}x{height}) is too small. "
            f"Minimum required: {MIN_PIXELS} pixels (e.g., 2560x1440)."
        ), None
    
    if total_pixels > MAX_PIXELS:
        return False, (
            f"Total pixels {total_pixels} ({width}x{height}) exceeds maximum. "
            f"Maximum allowed: {MAX_PIXELS} pixels (4096x4096)."
        ), None
    
    # 验证宽高比
    aspect_ratio = width / height
    
    if aspect_ratio < MIN_RATIO or aspect_ratio > MAX_RATIO:
        return False, (
            f"Aspect ratio {aspect_ratio:.4f} (width/height) is out of range. "
            f"Valid range: [{MIN_RATIO}, {MAX_RATIO}]."
        ), None
    
    # 判断方向
    if aspect_ratio > 1:
        orientation = 'landscape'
    elif aspect_ratio < 1:
        orientation = 'portrait'
    else:
        orientation = 'square'
    
    size_info = {
        'type': 'custom',
        'width': width,
        'height': height,
        'aspect_ratio': round(aspect_ratio, 4),
        'total_pixels': total_pixels,
        'orientation': orientation
    }
    
    return True, None, size_info


def get_size_info(size_str):
    """
    获取尺寸的详细信息 (兼容旧API)
    
    Args:
        size_str: 尺寸字符串
        
    Returns:
        dict: 尺寸信息
    """
    is_valid, error, size_info = validate_size(size_str)
    return size_info if is_valid else None


def download_image(image_url, output_path):
    """
    下载图片到本地
    
    Args:
        image_url: 图片URL
        output_path: 保存路径
        
    Returns:
        str: 保存路径
    """
    req = urllib.request.Request(image_url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; ImageDownloader/1.0)'
    })
    
    with urllib.request.urlopen(req, timeout=60) as response:
        with open(output_path, 'wb') as f:
            f.write(response.read())
    
    return output_path


def get_api_key():
    """
    从环境变量或配置文件中获取ARK_API_KEY
    
    Returns:
        str: API密钥或None
    """
    # 首先尝试从环境变量获取
    api_key = os.environ.get('ARK_API_KEY')
    if api_key:
        return api_key
    
    # 尝试从常见的配置文件中读取
    config_files = [
        os.path.expanduser('~/.zshrc'),
        os.path.expanduser('~/.bashrc'),
        os.path.expanduser('~/.bash_profile'),
        os.path.expanduser('~/.profile')
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('export ARK_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip().strip('"\'')
                            return api_key
            except Exception:
                continue
    
    return None


def get_volc_credentials():
    """
    获取火山引擎凭证 (用于veImageX API)
    
    Returns:
        dict: 包含ak, sk, service_id, domain, template的字典，或None
    """
    ak = os.environ.get('VOLC_AK')
    sk = os.environ.get('VOLC_SK')
    service_id = os.environ.get('VOLC_SERVICE_ID')
    domain = os.environ.get('VOLC_DOMAIN')
    template = os.environ.get('VOLC_TEMPLATE')
    
    if not all([ak, sk, service_id, domain, template]):
        return None
    
    return {
        'ak': ak,
        'sk': sk,
        'service_id': service_id,
        'domain': domain,
        'template': template
    }


def upload_image_to_get_url(image_path):
    """
    将本地图片上传并获取可访问的URL
    用于图生图功能中需要先将本地图片转为URL的情况
    
    Args:
        image_path: 本地图片路径
        
    Returns:
        str: 图片URL，或None如果上传失败
    """
    # 这里可以实现上传逻辑，比如上传到veImageX或其他图床
    # 简化版本：假设用户提供的图片已经是可访问的URL
    
    if image_path.startswith('http://') or image_path.startswith('https://'):
        return image_path
    
    # 如果是本地文件，需要上传
    # 这里返回None，让调用者处理上传逻辑
    return None


def validate_image_file(image_path):
    """
    验证图片文件是否有效
    
    Args:
        image_path: 图片路径
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, f"Image file not found: {image_path}"
    
    # 检查文件扩展名
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic', '.apng', '.ico', '.avif']
    ext = os.path.splitext(image_path)[1].lower()
    
    if ext not in valid_extensions:
        return False, f"Invalid image format: {ext}. Supported: {', '.join(valid_extensions)}"
    
    # 检查文件大小 (35MB限制)
    file_size = os.path.getsize(image_path)
    max_size = 35 * 1024 * 1024  # 35MB
    
    if file_size > max_size:
        return False, f"Image too large: {file_size / 1024 / 1024:.1f}MB. Maximum: 35MB"
    
    return True, None
