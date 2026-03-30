#!/usr/bin/env python3
"""
豆包文生图工具
使用火山引擎 Ark SDK 调用图片生成 API

安装依赖:
    pip install 'volcengine-python-sdk[ark]'

Usage:
    python3 generate_image.py "提示词" --size 2K
    python3 generate_image.py "一只可爱的猫咪" --size 3750x1250
    python3 generate_image.py "提示词" --size 4K --output ./my_image.jpg

Environment Variables:
    ARK_API_KEY: 火山引擎 API 密钥（必需）
"""

import argparse
import json
import os
import sys

# 导入共享工具
from image_utils import validate_size, get_size_info, download_image, get_api_key, generate_output_path


def generate_image(prompt, size="2K", output_path=None):
    """
    使用火山引擎 Ark SDK 生成图片 (文生图)
    
    Args:
        prompt: 图片生成提示词
        size: 图片尺寸 (如 "2K", "4K", "3750x1250")
        output_path: 可选，保存图片的路径
    
    Returns:
        dict: API响应结果，包含图片URL
    """
    # 延迟导入 SDK
    try:
        from volcenginesdkarkruntime import Ark
    except ImportError:
        print("❌ Error: volcengine-python-sdk not installed.", file=sys.stderr)
        print("Please install with: pip install 'volcengine-python-sdk[ark]'", file=sys.stderr)
        sys.exit(1)
    
    # 验证尺寸参数
    is_valid, error_msg, size_info = validate_size(size)
    if not is_valid:
        print(f"❌ Error: {error_msg}", file=sys.stderr)
        print("\n📏 Valid size examples:", file=sys.stderr)
        print("   Preset: 2K, 4K", file=sys.stderr)
        print("   Custom: 3750x1250, 2560x1440, 1440x2560", file=sys.stderr)
        sys.exit(1)
    
    # 获取API密钥
    api_key = get_api_key()
    if not api_key:
        print("❌ Error: ARK_API_KEY not found.", file=sys.stderr)
        print("Please set it with: export ARK_API_KEY=your_api_key", file=sys.stderr)
        print("Or add it to ~/.zshrc or ~/.bashrc", file=sys.stderr)
        sys.exit(1)
    
    # 创建 Ark 客户端
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    try:
        # 调用文生图 API
        response = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size=size,
            sequential_image_generation="disabled",
            response_format="url",
            watermark=False
        )
        
        # 构建结果字典
        result = {
            "url": response.data[0].url if response.data else None,
            "revised_prompt": response.data[0].revised_prompt if response.data and hasattr(response.data[0], 'revised_prompt') else None,
        }
        
        # 下载图片到本地（未指定路径时自动生成）
        if result['url']:
            save_path = output_path or generate_output_path("image")
            try:
                download_image(result['url'], save_path)
                result['saved_to'] = save_path
            except Exception as e:
                print(f"⚠️ Warning: Failed to download image: {e}", file=sys.stderr)
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate images using Doubao/Volces Ark API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Size Options (choose ONE method):

Method 1 - Preset Resolution:
  2K    High resolution (recommended for most cases)
  4K    Ultra high resolution
  
Method 2 - Custom Width x Height:
  Format: WIDTHxHEIGHT (e.g., 3750x1250, 2560x1440)
  
  Constraints:
  • Total pixels: 3,686,400 to 16,777,216
  • Aspect ratio: 1/16 to 16 (width/height)
  
  Valid examples:
  • 3750x1250   (landscape, 4.6M pixels)
  • 2560x1440   (landscape, 3.7M pixels)  
  • 1440x2560   (portrait, 3.7M pixels)
  • 2048x2048   (square, 4.2M pixels)
  
  Invalid examples:
  • 1500x1500   (too small, only 2.2M pixels)
  • 5000x5000   (too large, 25M pixels)

Examples:
    python3 generate_image.py "一只可爱的猫咪"
    python3 generate_image.py "星空下的城市" --size 4K
    python3 generate_image.py "宽屏风景" --size 3750x1250
    python3 generate_image.py "手机壁纸" --size 1440x2560 --output ./wallpaper.jpg

Environment Variables:
    ARK_API_KEY    Your Doubao API key (required)
        """
    )
    
    parser.add_argument('prompt', help='Image generation prompt (Chinese or English)')
    parser.add_argument('--size', '-s', default='2K',
                        help='Image size (default: 2K). Use "2K", "4K", or custom "WIDTHxHEIGHT". See examples below.')
    parser.add_argument('--output', '-o', 
                        help='Optional: Save image to specified path')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output raw JSON response')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate size parameter without generating')
    
    args = parser.parse_args()
    
    # 仅验证模式
    if args.validate_only:
        is_valid, error_msg, size_info = validate_size(args.size)
        if is_valid:
            print(f"✅ Size '{args.size}' is valid!")
            print(f"\n📐 Size Info:")
            for key, value in size_info.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Invalid size: {error_msg}")
            sys.exit(1)
        return
    
    # 生成图片
    result = generate_image(args.prompt, args.size, args.output)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("✅ Image generated successfully!")
        print(f"\n📝 Prompt: {args.prompt}")
        print(f"📐 Size: {args.size}")
        
        # 显示尺寸详情
        size_info = get_size_info(args.size)
        if size_info and size_info.get('type') == 'custom':
            print(f"   Dimensions: {size_info['width']}x{size_info['height']}")
            print(f"   Aspect Ratio: {size_info['aspect_ratio']}")
            print(f"   Total Pixels: {size_info['total_pixels']:,}")
        
        if result.get('url'):
            print(f"\n🔗 Image URL: {result['url']}")
        
        if result.get('saved_to'):
            print(f"💾 Saved to: {result['saved_to']}")
        
        if result.get('revised_prompt'):
            print(f"\n🔄 Revised Prompt: {result['revised_prompt']}")


if __name__ == '__main__':
    main()
