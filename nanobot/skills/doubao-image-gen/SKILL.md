---
name: doubao-image-gen
description: "Generate AI images using the Doubao (ByteDance/Volces) Ark API. Use when the user asks to create, draw, or generate images, illustrations, wallpapers, or artwork from text descriptions (Chinese or English). Also handles image-to-image transformations such as style transfer, background replacement, and outfit swapping. Supports preset sizes (2K, 4K) and custom dimensions."
metadata: {"nanobot":{"emoji":"🎨","requires":{"bins":["python3"],"env":["ARK_API_KEY"]},"install":[{"id":"pip","kind":"pip","package":"volcengine-python-sdk[ark]","label":"Install Ark SDK"}]}}
---

# Doubao Image Generation

Two modes: **text-to-image** and **image-to-image** via the Ark SDK.

## CRITICAL: File Path Rules

1. Always use `--json` when calling scripts.
2. Read the `saved_to` field from script output for the real file path. **NEVER fabricate paths.**
3. Use the exact `saved_to` path in the message `media` field.

## Text-to-Image

```bash
cd /path/to/doubao-image-gen && python3 scripts/generate_image.py "提示词" --json
```

Size options: `2K` (default), `4K`, or custom `WIDTHxHEIGHT` (e.g., `1440x2560`).

Custom size constraints: 3,686,400 to 16,777,216 total pixels, aspect ratio 1/16 to 16.

```bash
python3 scripts/generate_image.py "星空下的城市" --size 4K --json
python3 scripts/generate_image.py "手机壁纸，动漫风格" --size 1440x2560 --json
python3 scripts/generate_image.py "提示词" --output ./my_image.jpg --json
```

## Image-to-Image

Single image:
```bash
python3 scripts/img2img.py "将背景换成海滩" --image ./input.jpg --json
```

Multiple images (e.g., outfit swap):
```bash
python3 scripts/img2img.py "将图1的服装换为图2的服装" --image ./person.jpg --image ./clothing.jpg --json
```

Both local files and URLs are supported as `--image` inputs.

## JSON Output Format

```json
{
  "url": "https://...",
  "revised_prompt": "...",
  "saved_to": "/absolute/path/to/output/image_20260302_233626.jpg"
}
```

Images are auto-saved to `~/.nanobot/output/`. Use `--output` to override the save path.

## Prompt Tips

Build prompts with: **Subject + Details + Style + Lighting + Composition + Quality + Mood**.

Use 3-5 precise descriptors. Prefer professional photography/art terms (e.g., `85mm f/1.4`, `侧逆光`, `OC渲染`).

For detailed prompt engineering guidance and examples, see [references/prompt-guide.md](references/prompt-guide.md).

## Notes

- Generation takes 10-60 seconds depending on complexity
- Both Chinese and English prompts are supported
- Uses `doubao-seedream-4-5-251128` model
- Requires `ARK_API_KEY` environment variable
