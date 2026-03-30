# Prompt Engineering Guide

## Structure Formula

```
[主体] + [细节描述] + [艺术风格] + [光影/构图] + [渲染质量] + [氛围/情绪]
```

English: `[Subject] + [Details] + [Art Style] + [Lighting/Composition] + [Quality] + [Mood]`

## Key Elements

| Priority | Element | Example |
|----------|---------|---------|
| 1 | **Subject** | 一只橘猫在阳光下打盹 |
| 2 | **Details** | 毛发蓬松，琥珀色眼睛，白色爪尖 |
| 3 | **Style** | 吉卜力动画风格，水彩画 |
| 4 | **Lighting** | 金色夕阳光，侧光，柔和阴影 |
| 5 | **Composition** | 特写，45度角，浅景深 |
| 6 | **Quality** | 8K，OC渲染，超精细 |
| 7 | **Mood** | 温馨，治愈，宁静祥和 |

## Best Practices

### 1. Concise over verbose

Use 3-5 precise adjectives. Avoid repeating the same feature.

Bad: `超级非常特别极其美丽的漂亮的花朵在阳光下闪闪发光非常好看`
Good: `香槟玫瑰，花瓣边缘微卷，晨露点缀，金色侧逆光，浅景深，8K超清`

### 2. Professional terminology

| Category | Terms |
|----------|-------|
| **Lens** | 50mm定焦, 85mm人像, 广角, 微距, 长焦 |
| **Aperture** | f/1.2大光圈, f/2.8, f/8小光圈 |
| **Lighting** | 伦勃朗光, 蝴蝶光, 侧逆光, 轮廓光, 体积光 |
| **Style** | 印象派, 赛博朋克, 极简主义, 新艺术运动 |
| **Rendering** | OC渲染, 光线追踪, PBR材质, 全局光照 |

### 3. Style reference formula

```
[主体], in the style of [艺术家/流派], [媒介], [年代/地域特征]
```

Example: `山间古寺，传统水墨画风格，张大千笔触，留白意境，雾气缭绕，宣纸质感`

### 4. Photography template

```
[主体], shot with [相机] + [镜头] at [光圈], [光线条件], [构图], [景深], [胶片/滤镜效果], [画质]
```

Example: `街头艺人演奏小提琴，Sony A7R4 + 85mm f/1.4，金色夕阳光，三分法构图，背景虚化，电影感调色，8K RAW质感`

## Text-to-Image vs Image-to-Image

**Text-to-Image**: Describe all elements from scratch. For creative concepts, illustrations, scene design.

**Image-to-Image**: Focus on modification instructions only. Specify "keep XX, change YY". For editing, style transfer, local modifications.

## Prompt Length Guidelines

| Task Type | Recommended Length |
|-----------|-------------------|
| Simple objects | 10-20 words |
| Complex scenes | 30-60 words |
| Professional work | 40-80 words |

## Style Keywords

- **Classical**: Renaissance, Baroque, Rococo, Neoclassical
- **Modern**: Art Nouveau, Art Deco, Bauhaus, Pop Art
- **Digital**: Concept art, Matte painting, Digital illustration, 3D render
- **Photography**: Film noir, Documentary, Fashion, Minimalist
- **Anime/Manga**: Ghibli, 90s anime, Shonen, Chibi
- **Chinese**: Gongbi, Ink wash, Shan shui, New Year painting

## Example Prompts

**Sci-Fi:**
```
星际穿越场景，巨型黑洞吸积盘发出耀眼光芒，一艘破损的复古蒸汽朋克飞船正被引力拉扯变形，金属碎片飘散，电影级宽屏构图，光线追踪渲染，超现实主义风格，深蓝与橙红对比色，8K超高清
```

**Portrait:**
```
一位亚洲女性，柔和自然光从侧面洒落，浅景深背景虚化，穿着简约米色针织衫，温暖色调，专业人像摄影风格，Sony A7R4 + 85mm f/1.4拍摄，8K画质
```

**Chinese Ink:**
```
山水意境，传统水墨画风格，留白构图，远山如黛，近水含烟，一叶扁舟，张大千笔触，宣纸纹理，黑白灰层次，禅意氛围
```

**Cyberpunk:**
```
未来都市夜景，霓虹灯招牌闪烁，雨中街道反射彩色光芒，赛博朋克风格，全息广告牌，蓝紫色调为主，电影级构图，OC渲染，8K超清细节
```
