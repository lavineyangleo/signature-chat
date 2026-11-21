from io import BytesIO
from pathlib import Path
from PIL import Image, ImageChops, ImageOps


def transparent_signature(source: bytes | Path, target: Path) -> dict:
    """Extract black ink from white/transparent artwork, keeping soft stroke edges.

    This is specifically a monochrome signature matte, not general photo segmentation.
    Alpha = (255 - luminance) * existing_alpha / 255; near-white noise is removed.
    """
    with Image.open(BytesIO(source) if isinstance(source, bytes) else source) as opened:
        if opened.width * opened.height > 25_000_000:
            raise ValueError('图片超过2500万像素限制。')
        rgba = opened.convert('RGBA')
    ink = ImageOps.invert(ImageOps.grayscale(rgba.convert('RGB')))
    ink = ink.point(lambda value: 0 if value <= 10 else value)
    alpha = ImageChops.multiply(ink, rgba.getchannel('A'))
    low, high = alpha.getextrema()
    transparent_count = alpha.histogram()[0]
    edges = [(0, 0, alpha.width, 1), (0, alpha.height - 1, alpha.width, alpha.height),
             (0, 0, 1, alpha.height), (alpha.width - 1, 0, alpha.width, alpha.height)]
    edge_zero = sum(alpha.crop(box).histogram()[0] for box in edges)
    if low != 0 or high < 32 or transparent_count < alpha.width * alpha.height * 0.05 or edge_zero < (alpha.width + alpha.height) * 2 * 0.75:
        raise ValueError('图片没有可验证的透明背景或有效笔迹，未导出。')
    output = Image.new('RGBA', rgba.size, (0, 0, 0, 0))
    output.putalpha(alpha)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix('.tmp')
    output.save(temp, format='PNG', optimize=True)
    temp.replace(target)
    return {'width': output.width, 'height': output.height, 'format': 'PNG',
            'mode': 'RGBA', 'alpha_min': low, 'alpha_max': high,
            'transparent_pixels': transparent_count, 'processing': 'black-ink-alpha-v1'}
