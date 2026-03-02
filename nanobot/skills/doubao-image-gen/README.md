# 豆包图片生成工具 (Doubao Image Generation)

使用火山引擎 Ark SDK 的图片生成工具，支持文生图和图生图功能。

## 功能特性

- ✅ **文生图 (Text-to-Image)** - 通过文字描述生成图片
- ✅ **图生图 (Image-to-Image)** - 基于单张或多张参考图片进行编辑和转换
- ✅ **单图生成** - 使用单张图片作为参考进行生成
- ✅ **多图生成** - 使用多张图片作为输入（如换装、融合等场景）
- ✅ **尺寸验证** - 自动验证并提示图片尺寸是否符合 API 要求
- ✅ **预设尺寸** - 支持 2K/4K 预设和自定义尺寸
- ✅ **图片下载** - 自动生成后可选下载到本地

## 文件结构

```
scripts/
├── generate_image.py    # 文生图主脚本
├── img2img.py          # 图生图主脚本（支持单图/多图）
├── image_utils.py      # 共享工具函数
└── requirements.txt    # Python 依赖

SKILL.md                # 完整使用文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install 'volcengine-python-sdk[ark]'
```

### 2. 配置环境变量

```bash
export ARK_API_KEY=your_api_key_here
```

### 3. 文生图

```bash
# 基本用法（默认2K分辨率）
python3 scripts/generate_image.py "一只可爱的猫咪在草地上玩耍"

# 指定分辨率
python3 scripts/generate_image.py "星空下的城市" --size 4K

# 自定义尺寸
python3 scripts/generate_image.py "手机壁纸" --size 1440x2560 --output ./wallpaper.jpg
```

### 4. 图生图

```bash
# 单图生成
python3 scripts/img2img.py "将背景换成海滩" --image ./input.jpg

# 多图生成（如换装）
python3 scripts/img2img.py "将图1的服装换为图2的服装" \
    --image ./person.jpg \
    --image ./clothing.jpg

# 指定输出尺寸和保存路径
python3 scripts/img2img.py "添加星空效果" \
    --image ./input.jpg \
    --size 2K \
    --output ./output.jpg

# 从URL生成
python3 scripts/img2img.py "改变风格" --image https://example.com/image.jpg
```

## 环境变量配置

```bash
export ARK_API_KEY=your_api_key_here
```

**获取 API Key:** https://console.volcengine.com/ark/region:ark+cn-beijing/apikey

## 尺寸规范

### 文生图 & 图生图

- **预设**: `2K`, `4K`
- **自定义**: `WIDTHxHEIGHT`（例如：`3750x1250`）
- **像素范围**: 3,686,400 到 16,777,216
- **宽高比**: 1/16 到 16

**推荐尺寸:**

| 尺寸 | 总像素 | 宽高比 | 适用场景 |
|------|--------|--------|----------|
| `2K` | 预设 | - | 通用（推荐） |
| `4K` | 预设 | - | 高画质需求 |
| `3750x1250` | 4.6M | 3:1 | 超宽屏海报 |
| `2560x1440` | 3.7M | 16:9 | 桌面壁纸 |
| `1440x2560` | 3.7M | 9:16 | 手机壁纸 |
| `2048x2048` | 4.2M | 1:1 | 方形图 |

## API 文档

- [Ark SDK 文档](https://www.volcengine.com/docs/82379/1268742)
- [文生图 API 参考](https://ark.cn-beijing.volces.com/api/v3/images/generations)

## 使用提示

### 有效的提示词结构

1. **主体** - 主要焦点是什么？
2. **细节** - 外观、材质、颜色、特征
3. **风格** - 艺术风格（如：超现实主义、赛博朋克）
4. **光影** - 光线条件（如：光线追踪、动态模糊）
5. **质量** - 渲染质量（如：OC渲染、8K画质）
6. **氛围** - 情绪和感觉（如：末日既视感、暗黑风）

### 文生图示例提示词

**科幻场景:**
```
星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，
抢视觉冲击力，电影大片，末日既视感，动感，对比色，
oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝
```

### 图生图示例提示词

**风格转换:**
```
将背景换成日落海滩，金色阳光，温暖的色调
保持人物不变，添加梦幻光晕效果
```

**换装（多图）:**
```
将图1的服装换为图2的服装
```

## 注意事项

- 需要先安装 `pip install 'volcengine-python-sdk[ark]'`
- 图片生成可能需要 10-60 秒，请耐心等待
- 生成的图片 URL 是临时的，请及时下载保存
- 支持本地文件和 URL 作为图生图的输入
- 支持的图片格式：jpg, jpeg, png, webp, bmp, heic

## 技术细节

- **SDK**: `volcengine-python-sdk[ark]`
- **模型**: `doubao-seedream-4-5-251128`
- **API Base**: `https://ark.cn-beijing.volces.com/api/v3`
