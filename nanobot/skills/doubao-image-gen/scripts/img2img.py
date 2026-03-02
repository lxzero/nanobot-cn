#!/usr/bin/env python3
"""
豆包图生图工具
使用火山引擎 Ark SDK 调用图片生成 API

安装依赖:
    pip install 'volcengine-python-sdk[ark]'

Usage:
    # 单图生图
    python3 img2img.py "将背景换成海滩" --image ./input.jpg
    python3 img2img.py "添加星空效果" --image ./input.jpg --size 2K
    
    # 多图生图 (如换装)
    python3 img2img.py "将图1的服装换为图2的服装" --image ./person.jpg --image ./clothing.jpg
    
    # 从 URL 生图
    python3 img2img.py "转换成油画风格" --image https://example.com/image.png

Environment Variables:
    ARK_API_KEY: 火山引擎 API 密钥（必需）
"""

import argparse
import json
import os
import sys

# 导入共享工具
from image_utils import validate_size, get_size_info, download_image, get_api_key, generate_output_path


def img2img_single(image, prompt, size="2K", output_path=None):
    """
    使用火山引擎 Ark SDK 进行单图生图
    
    Args:
        image: 输入图片路径或URL
        prompt: 图片转换提示词
        size: 输出尺寸 (如 "2K", "4K", "3750x1250")
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
    
    # 处理图片路径
    image_url = image
    if not image.startswith(('http://', 'https://')):
        # 本地文件需要转换为 data URL
        import base64
        try:
            with open(image, 'rb') as f:
                image_data = f.read()
            ext = os.path.splitext(image)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp',
                '.heic': 'image/heic',
            }.get(ext, 'image/jpeg')
            image_url = f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}"
        except Exception as e:
            print(f"❌ Error reading image: {e}", file=sys.stderr)
            sys.exit(1)
    
    # 创建 Ark 客户端
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    try:
        # 调用图生图 API (单图)
        response = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            image=image_url,
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
            save_path = output_path or generate_output_path("img2img")
            try:
                download_image(result['url'], save_path)
                result['saved_to'] = save_path
            except Exception as e:
                print(f"⚠️ Warning: Failed to download image: {e}", file=sys.stderr)
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def img2img_multi(images, prompt, size="2K", output_path=None):
    """
    使用火山引擎 Ark SDK 进行多图生图
    
    Args:
        images: 输入图片路径或URL列表
        prompt: 图片转换提示词
        size: 输出尺寸 (如 "2K", "4K", "3750x1250")
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
    
    # 处理图片路径
    import base64
    image_urls = []
    for image in images:
        if image.startswith(('http://', 'https://')):
            image_urls.append(image)
        else:
            # 本地文件需要转换为 data URL
            try:
                with open(image, 'rb') as f:
                    image_data = f.read()
                ext = os.path.splitext(image)[1].lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.bmp': 'image/bmp',
                    '.heic': 'image/heic',
                }.get(ext, 'image/jpeg')
                image_urls.append(f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}")
            except Exception as e:
                print(f"❌ Error reading image {image}: {e}", file=sys.stderr)
                sys.exit(1)
    
    # 创建 Ark 客户端
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    try:
        # 调用图生图 API (多图)
        response = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            image=image_urls,
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
            save_path = output_path or generate_output_path("img2img_multi")
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
        description='Image-to-image generation using Doubao/Volces Ark API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  1. Single Image:  Provide one --image argument
  2. Multi-Image:   Provide multiple --image arguments (e.g., for outfit swap)

Size Options (choose ONE method):

Method 1 - Preset Resolution:
  2K    High resolution (recommended for most cases)
  4K    Ultra high resolution
  
Method 2 - Custom Width x Height:
  Format: WIDTHxHEIGHT (e.g., 3750x1250, 2560x1440)
  
  Constraints:
  • Total pixels: 3,686,400 to 16,777,216
  • Aspect ratio: 1/16 to 16 (width/height)

Examples:
    # Single image transformation
    python3 img2img.py "将背景换成海滩" --image ./input.jpg
    python3 img2img.py "添加星空效果" --image ./input.jpg --size 2K
    python3 img2img.py "转换成油画风格" --image ./input.jpg --output ./output.jpg
    
    # Multiple images (e.g., outfit swap)
    python3 img2img.py "将图1的服装换为图2的服装" --image ./person.jpg --image ./clothing.jpg
    
    # From URL
    python3 img2img.py "改变风格" --image https://example.com/image.png --size 2K

Environment Variables:
    ARK_API_KEY    Your Doubao API key (required)
        """
    )
    
    parser.add_argument('prompt', help='Image transformation prompt (Chinese or English)')
    parser.add_argument('--image', '-i', action='append', required=True,
                        help='Input image path or URL. Can be specified multiple times for multi-image generation.')
    parser.add_argument('--size', '-s', default='2K',
                        help='Output size (default: 2K). Use "2K", "4K", or custom "WIDTHxHEIGHT".')
    parser.add_argument('--output', '-o', 
                        help='Save output image to specified path')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output raw JSON response')
    
    args = parser.parse_args()
    
    # 根据图片数量选择模式
    if len(args.image) == 1:
        # 单图模式
        result = img2img_single(
            image=args.image[0],
            prompt=args.prompt,
            size=args.size,
            output_path=args.output
        )
        mode = "Single Image"
    else:
        # 多图模式
        result = img2img_multi(
            images=args.image,
            prompt=args.prompt,
            size=args.size,
            output_path=args.output
        )
        mode = f"Multi-Image ({len(args.image)} images)"
    
    # 输出结果
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("✅ Image-to-image generation successful!")
        print(f"\n📝 Prompt: {args.prompt}")
        print(f"📐 Mode: {mode}")
        print(f"📐 Output Size: {args.size}")
        
        # 显示尺寸详情
        size_info = get_size_info(args.size)
        if size_info and size_info.get('type') == 'custom':
            print(f"   Dimensions: {size_info['width']}x{size_info['height']}")
            print(f"   Aspect Ratio: {size_info['aspect_ratio']}")
            print(f"   Total Pixels: {size_info['total_pixels']:,}")
        
        if result.get('url'):
            print(f"\n🔗 Result URL: {result['url']}")
        
        if result.get('saved_to'):
            print(f"💾 Saved to: {result['saved_to']}")
        
        if result.get('revised_prompt'):
            print(f"\n🔄 Revised Prompt: {result['revised_prompt']}")


if __name__ == '__main__':
    main()
