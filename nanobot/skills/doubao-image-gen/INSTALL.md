# Doubao Image Generation Skill 安装说明

## 安装步骤

### 1. 安装依赖

```bash
pip install 'volcengine-python-sdk[ark]'
```

### 2. 配置环境变量

设置 ARK_API_KEY 环境变量：

```bash
# 临时设置（当前终端会话有效）
export ARK_API_KEY=your_api_key_here

# 永久设置（添加到shell配置文件）
echo 'export ARK_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

**获取 API Key:** https://console.volcengine.com/ark/region:ark+cn-beijing/apikey

## 使用方法

### 直接使用脚本

```bash
# 基础使用（默认2K分辨率）
python3 scripts/generate_image.py "一只可爱的猫咪"

# 指定尺寸
python3 scripts/generate_image.py "星空下的城市" --size 4K

# 保存到文件
python3 scripts/generate_image.py "提示词" --size 2K --output ./my_image.jpg

# JSON格式输出
python3 scripts/generate_image.py "提示词" --json
```

### 图生图（单图）

```bash
python3 scripts/img2img.py "将背景换成海滩" --image ./input.jpg --size 2K
```

### 图生图（多图）

```bash
python3 scripts/img2img.py "将图1的服装换为图2的服装" \
    --image ./person.jpg \
    --image ./clothing.jpg \
    --size 2K
```

### 支持的尺寸

- `2K` - 高清分辨率（默认，推荐）
- `4K` - 超高清分辨率
- `3750x1250` - 宽屏横版
- `2560x1440` - 16:9 横版
- `1440x2560` - 9:16 竖版
- 其他自定义尺寸（总像素 3,686,400 - 16,777,216）

### 示例提示词

**科幻场景：**
```bash
python3 scripts/generate_image.py "星际穿越，黑洞，超现实主义风格，电影大片质感"
```

**人物肖像：**
```bash
python3 scripts/generate_image.py "一位亚洲女性，穿着现代时尚服装，柔和的自然光，专业摄影风格"
```

## 在Python中调用

```python
import sys
sys.path.insert(0, 'scripts')
from generate_image import generate_image

# 文生图
result = generate_image(
    prompt="星际穿越，黑洞，超现实主义风格",
    size="2K"
)
print(result['url'])
```

```python
from img2img import img2img_single, img2img_multi

# 单图生图
result = img2img_single(
    image="./input.jpg",
    prompt="将背景换成夕阳下的海滩",
    size="2K"
)

# 多图生图
result = img2img_multi(
    images=["./person.jpg", "./clothing.jpg"],
    prompt="将图1的服装换为图2的服装",
    size="2K"
)
```

## 功能特性

- ✅ 支持中英文提示词
- ✅ 多种分辨率可选（2K、4K、自定义）
- ✅ 文生图和图生图（单图/多图）
- ✅ 自动生成图片URL
- ✅ 可选保存到本地文件
- ✅ JSON格式输出
- ✅ 详细的错误提示
- ✅ 支持本地文件和URL作为输入

## 注意事项

1. **必须设置 ARK_API_KEY 环境变量**，否则无法使用
2. 需要先安装 `volcengine-python-sdk[ark]`
3. 图片生成可能需要 10-60 秒，请耐心等待
4. 生成的图片 URL 有有效期，请及时下载保存
5. 建议在网络稳定的环境下使用

## 故障排查

### 错误：SDK Not Installed
```
❌ Error: volcengine-python-sdk not installed.
```
**解决**: 执行 `pip install 'volcengine-python-sdk[ark]'`

### 错误：ARK_API_KEY not found
```
❌ Error: ARK_API_KEY not found.
```
**解决**: 执行 `export ARK_API_KEY=your_api_key`

### 错误：HTTP 401 Unauthorized
**解决**: 检查 API 密钥是否正确

### 错误：HTTP 429 Too Many Requests
**解决**: 稍等片刻再试，避免频繁请求
