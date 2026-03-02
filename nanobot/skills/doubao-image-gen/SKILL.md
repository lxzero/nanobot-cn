---
name: doubao-image-gen
description: Generate images using Doubao/Volces Ark API with comprehensive size validation. Use when the user needs to create AI-generated images with Chinese or English prompts. Supports preset sizes (2K, 4K) and custom dimensions with automatic validation. Includes text-to-image and image-to-image generation capabilities. Requires ARK_API_KEY environment variable.
---

# Doubao Image Generation

Generate high-quality AI images using the Doubao (ByteDance/Volces) image generation API through the official Ark SDK.

## Overview

This skill provides image generation capabilities through the Ark API:

1. **Text-to-Image (文生图)** - Generate images from text prompts
2. **Image-to-Image (图生图)** - Transform existing images (single or multiple) based on text prompts

## CRITICAL: Agent Usage Rules

When using this skill to generate images, you **MUST** follow these rules:

1. **Always use `--json` flag** when calling the scripts, so you can parse the structured output.
2. **Read the actual script output** to get the real `saved_to` file path. **NEVER fabricate or guess file paths.**
3. Images are **auto-saved** to the `output/` directory under the skill root. The actual path is printed in the script output as `saved_to`.
4. **Use the exact `saved_to` path** from the script's JSON output in the `media` field of your message.

### Correct Workflow Example

```bash
# Step 1: Generate image with --json flag
cd /path/to/doubao-image-gen && python3 scripts/generate_image.py "提示词" --json
```

The JSON output will look like:
```json
{
  "url": "https://...",
  "revised_prompt": "...",
  "saved_to": "/path/to/doubao-image-gen/output/image_20260302_233626.jpg"
}
```

Then use the **actual** `saved_to` path from the output in your message's `media` field.

### Common Mistakes to Avoid

- **DO NOT** guess or fabricate output file paths — always read them from script output
- **DO NOT** send the message before confirming the file was saved successfully
- **DO NOT** use the remote URL in the `media` field — use the local `saved_to` path

## Prerequisites

### Install Dependencies

```bash
pip install 'volcengine-python-sdk[ark]'
```

### Set API Key

Set the `ARK_API_KEY` environment variable:

```bash
export ARK_API_KEY=your_api_key_here
```

To make it permanent, add to your `~/.zshrc` or `~/.bashrc`.

**Get API Key:** https://console.volcengine.com/ark/region:ark+cn-beijing/apikey

## Text-to-Image Usage

### Size Options

#### Method 1: Preset Resolution

| Size | Description |
|------|-------------|
| `2K` | High resolution (recommended for most use cases) |
| `4K` | Ultra high resolution |

**Example:**
```bash
python3 scripts/generate_image.py "宽屏电影海报，科幻风格" --size 2K
```

#### Method 2: Custom Dimensions

**Format:** `WIDTHxHEIGHT` (e.g., `3750x1250`)

**Constraints:**
- Total Pixels: 3,686,400 to 16,777,216
- Aspect Ratio: 1/16 to 16

**Valid Examples:**
| Size | Total Pixels | Aspect Ratio | Type |
|------|--------------|--------------|------|
| `3750x1250` | 4,687,500 | 3.0 | Landscape (Wide) |
| `2560x1440` | 3,686,400 | 1.78 | Landscape (16:9) |
| `1440x2560` | 3,686,400 | 0.56 | Portrait (9:16) |
| `2048x2048` | 4,194,304 | 1.0 | Square |

### Basic Text-to-Image

```bash
# Default 2K resolution
python3 scripts/generate_image.py "一只可爱的猫咪在草地上玩耍"

# Specify size
python3 scripts/generate_image.py "星空下的城市" --size 4K

# Custom dimensions
python3 scripts/generate_image.py "手机壁纸，动漫风格" --size 1440x2560

# Save to file
python3 scripts/generate_image.py "提示词" --size 2K --output ./my_image.jpg
```

## Image-to-Image Usage

Image-to-image generation transforms existing images based on a text prompt. Supports both single and multiple input images.

### Single Image-to-Image

Transform one image:

```bash
python3 scripts/img2img.py "将背景换成海滩" --image ./input.jpg
```

### Multiple Images-to-Image

Use multiple images as input (e.g., for outfit swapping):

```bash
python3 scripts/img2img.py "将图1的服装换为图2的服装" --image ./person.jpg --image ./clothing.jpg
```

### Specify Output Size

```bash
python3 scripts/img2img.py "添加星空效果" --image ./input.jpg --size 2K
```

### Save to File

```bash
python3 img2img.py "转换成油画风格" --image ./input.jpg --output ./output.jpg
```

### Using Image URLs

Both local files and URLs are supported:

```bash
python3 scripts/img2img.py "改变风格" --image https://example.com/image.jpg
```

## Python API

### Text-to-Image

```python
import sys
sys.path.insert(0, 'scripts')
from generate_image import generate_image, validate_size

# Validate size first
is_valid, error = validate_size("3750x1250")
if is_valid:
    result = generate_image(
        prompt="星际穿越，黑洞，超现实主义风格",
        size="3750x1250"
    )
    print(result['url'])
```

### Image-to-Image (Single)

```python
import sys
sys.path.insert(0, 'scripts')
from img2img import img2img_single

result = img2img_single(
    image="./input.jpg",
    prompt="将背景换成夕阳下的海滩",
    size="2K"
)
print(result['url'])
```

### Image-to-Image (Multiple)

```python
import sys
sys.path.insert(0, 'scripts')
from img2img import img2img_multi

result = img2img_multi(
    images=["./person.jpg", "./clothing.jpg"],
    prompt="将图1的服装换为图2的服装",
    size="2K"
)
print(result['url'])
```

## Prompt Engineering Guide

### Prompt Structure Formula

A high-quality AI image prompt should follow this structure:

```
[主体] + [细节描述] + [艺术风格] + [光影/构图] + [渲染质量] + [氛围/情绪]
```

**For English:**
```
[Subject] + [Details] + [Art Style] + [Lighting/Composition] + [Quality] + [Mood]
```

### Key Elements (按优先级排序)

| 优先级 | 元素 | 说明 | 示例 |
|--------|------|------|------|
| 1 | **主体 (Subject)** | 核心对象+动作+位置 | 一只橘猫在阳光下打盹 |
| 2 | **细节 (Details)** | 外观、材质、颜色、特征 | 毛发蓬松，琥珀色眼睛，白色爪尖 |
| 3 | **风格 (Style)** | 艺术流派/媒介/艺术家 | 吉卜力动画风格，水彩画 |
| 4 | **光影 (Lighting)** | 光源类型、时间、效果 | 金色夕阳光，侧光，柔和阴影 |
| 5 | **构图 (Composition)** | 视角、镜头、取景 | 特写，45度角，浅景深 |
| 6 | **质量 (Quality)** | 分辨率、渲染引擎 | 8K，OC渲染，超精细 |
| 7 | **氛围 (Mood)** | 情感、色调、感觉 | 温馨，治愈，宁静祥和 |

### Doubao/Seedream 提示词最佳实践

#### 1. 简洁优于堆砌

研究表明，**3-5个精准形容词**比大量华丽词汇效果更好。避免重复描述同一特征。

**❌ 不推荐：**
```
超级非常特别极其美丽的漂亮的花朵在阳光下闪闪发光非常好看
```

**✅ 推荐：**
```
香槟玫瑰，花瓣边缘微卷，晨露点缀，金色侧逆光，浅景深，8K超清
```

#### 2. 专业术语提升质量

使用摄影/艺术专业术语能显著提升图像专业度：

| 类别 | 术语示例 |
|------|---------|
| **镜头** | 50mm定焦, 85mm人像, 广角, 微距, 长焦 |
| **光圈** | f/1.2大光圈, f/2.8, f/8小光圈 |
| **光线** | 伦勃朗光, 蝴蝶光, 侧逆光, 轮廓光, 体积光 |
| **风格** | 印象派, 赛博朋克, 极简主义, 新艺术运动 |
| **渲染** | OC渲染, 光线追踪, PBR材质, 全局光照 |

#### 3. 风格参考公式

```
[主体], in the style of [艺术家/流派], [媒介], [年代/地域特征]
```

**示例：**
```
山间古寺，传统水墨画风格，张大千笔触，留白意境，雾气缭绕，宣纸质感
```

#### 4. 摄影类提示词模板

```
[主体], shot with [相机] + [镜头] at [光圈], [光线条件], 
[构图], [景深], [胶片/滤镜效果], [画质]
```

**示例：**
```
街头艺人演奏小提琴，Sony A7R4 + 85mm f/1.4，金色夕阳光，
三分法构图，背景虚化，电影感调色，8K RAW质感
```

### 文生图 vs 图生图提示词差异

#### 文生图 (Text-to-Image)
- 需要完整描述画面所有元素
- 强调从零构建场景
- 适合：创意概念、插画、场景设计

#### 图生图 (Image-to-Image)
- 聚焦**修改指令**，不需要重复描述保留部分
- 明确指定"保留XX，改变YY"
- 适合：图像编辑、风格迁移、局部修改

**图生图提示词示例：**
```bash
# 保留人物，改变背景
python3 scripts/img2img.py "人物保持不变，将背景换成东京涩谷夜景，霓虹灯闪烁" --image ./portrait.jpg

# 风格转换
python3 scripts/img2img.py "转换成莫奈印象派风格，朦胧笔触，花园光影" --image ./photo.jpg

# 添加元素
python3 scripts/img2img.py "原图不变，在人物手中添加一杯冒着热气的咖啡" --image ./input.jpg
```

### 提示词优化检查清单

在提交前，检查你的提示词是否包含：

- [ ] **主体清晰**：核心对象是什么？在做什么？
- [ ] **细节具体**：颜色、材质、纹理有描述吗？
- [ ] **风格明确**：指定了艺术风格或参考艺术家吗？
- [ ] **光影完整**：光源方向、时间、氛围光效？
- [ ] **构图合理**：视角、镜头类型、画面比例？
- [ ] **质量要求**：分辨率、渲染质量关键词？
- [ ] **无冲突描述**：避免"写实"和"卡通"同时出现

### Prompt Tips (Original)

### Example Prompts

#### 科幻场景 (Sci-Fi)
```
星际穿越场景，巨型黑洞吸积盘发出耀眼光芒，一艘破损的复古蒸汽朋克飞船
正被引力拉扯变形，金属碎片飘散，电影级宽屏构图，光线追踪渲染，
超现实主义风格，深蓝与橙红对比色，8K超高清，末日既视感
```

#### 人像摄影 (Portrait)
```
一位亚洲女性，柔和自然光从侧面洒落，浅景深背景虚化，
穿着简约米色针织衫，温暖色调，专业人像摄影风格，
Sony A7R4 + 85mm f/1.4拍摄，8K画质，逼真的皮肤质感，
宁静祥和的表情，工作室灯光
```

#### 风景插画 (Landscape Illustration)
```
富士山日出，樱花盛开季节，粉色花瓣飘落，湖面倒影如镜，
Golden Hour光线，水彩画风格，吉卜力动画色调，
全景构图，超高清细节，宁静治愈氛围
```

#### 产品摄影 (Product Photography)
```
极简护肤品瓶，玻璃磨砂质感，柔和的工作室灯光，
白色纯净背景，微距摄影，产品居中构图，
高端商业广告风格，8K渲染，反射细节清晰
```

#### 图生图转换 (Image-to-Image)
```
将背景换成日落海滩场景，金色阳光洒落，
人物保持原样不变，添加梦幻光晕效果，
温暖色调，电影感调色
```

#### 赛博朋克风格 (Cyberpunk)
```
未来都市夜景，霓虹灯招牌闪烁，雨中街道反射彩色光芒，
赛博朋克风格，全息广告牌，飞行汽车掠过，
蓝紫色调为主，电影级构图，OC渲染，
雨雾氛围，8K超清细节
```

#### 国风水墨 (Chinese Ink)
```
山水意境，传统水墨画风格，留白构图，
远山如黛，近水含烟，一叶扁舟，
张大千笔触，宣纸纹理，黑白灰层次，
禅意氛围，极简主义
```

### Common Use Cases

### Mobile Wallpaper (Text-to-Image)
```bash
python3 scripts/generate_image.py "抽象艺术壁纸，紫色渐变，简洁" --size 1440x2560
```

### Desktop Wallpaper (Text-to-Image)
```bash
python3 scripts/generate_image.py "科幻城市夜景，霓虹灯" --size 2560x1440
```

### Photo Style Transfer (Image-to-Image)
```bash
python3 scripts/img2img.py "转换成梵高油画风格，星空笔触" --image ./photo.jpg
```

### Background Replacement (Image-to-Image)
```bash
python3 scripts/img2img.py "将背景换成现代城市天际线，夜晚灯光" --image ./portrait.jpg
```

### Outfit Swap (Multi-Image)
```bash
python3 scripts/img2img.py "将图1的服装换为图2的服装" --image ./person.jpg --image ./clothing.jpg
```

## Error Handling

### SDK Not Installed
```
❌ Error: volcengine-python-sdk not installed.
Please install with: pip install 'volcengine-python-sdk[ark]'
```

### Invalid Size Format
```
❌ Error: Invalid size format: 'invalid'. Use '2K', '4K', or 'WIDTHxHEIGHT'
```

### Missing API Key
```
❌ Error: ARK_API_KEY not found.
Please set it with: export ARK_API_KEY=your_api_key
```

### Invalid Image Format
```
❌ Error reading image: [Errno 2] No such file or directory: './input.jpg'
```

## Resources

- `scripts/generate_image.py` - Text-to-image generation
- `scripts/img2img.py` - Image-to-image generation (single and multi-image)
- `scripts/image_utils.py` - Shared utilities

## Advanced Tips

### Iterative Prompt Refinement

Don't expect perfect results on the first try. Use this workflow:

1. **Start** with a basic prompt covering main elements
2. **Analyze** the output for strengths and weaknesses
3. **Refine** specific elements (add details, adjust style, modify lighting)
4. **Repeat** until satisfied

### Prompt Length Guidelines

| Task Type | Recommended Length | Notes |
|-----------|-------------------|-------|
| Simple objects | 10-20 words | Focus on key features |
| Complex scenes | 30-60 words | Balance detail and clarity |
| Professional work | 40-80 words | Include technical parameters |

### Avoiding Common Issues

| Issue | Solution |
|-------|----------|
| Inconsistent style | Remove conflicting descriptors |
| Wrong composition | Add specific framing terms (close-up, wide shot) |
| Poor anatomy | Add "correct anatomy" or reference pose terms |
| Blurry details | Include "8K", "ultra detailed", "sharp focus" |

### Style Reference Examples

Use these keywords to guide the artistic direction:

- **Classical**: Renaissance, Baroque, Rococo, Neoclassical
- **Modern**: Art Nouveau, Art Deco, Bauhaus, Pop Art
- **Digital**: Concept art, Matte painting, Digital illustration, 3D render
- **Photography**: Film noir, Documentary, Fashion, Minimalist
- **Anime/Manga**: Ghibli, 90s anime, Shonen, Chibi
- **Chinese**: Gongbi, Ink wash, Shan shui, New Year painting

## Notes

- Image generation may take 10-60 seconds depending on complexity
- Generated images are hosted temporarily; download promptly if needed
- Input images for image-to-image can be local files (converted to data URL) or remote URLs
- Both Chinese and English prompts are supported
- Uses `doubao-seedream-4-5-251128` model via Ark API
