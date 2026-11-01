"""PNG -> N64 texture encoders (replacement for n64tex.exe, byte-identical output)."""
from PIL import Image


def _pixels(img, mode):
    img = img.convert(mode)
    try:
        return list(img.get_flattened_data())
    except AttributeError:
        return list(img.getdata())


def rgba5551(path):
    out = bytearray()
    for r, g, b, a in _pixels(Image.open(path), 'RGBA'):
        v = ((r >> 3) << 11) | ((g >> 3) << 6) | ((b >> 3) << 1) | (1 if a != 0 else 0)
        out += v.to_bytes(2, 'big')
    return bytes(out)


def i4(path):
    px = _pixels(Image.open(path), 'LA')
    out = bytearray()
    for k in range(0, len(px), 2):
        hi = px[k][0] >> 4
        lo = px[k + 1][0] >> 4 if k + 1 < len(px) else 0
        out.append((hi << 4) | lo)
    return bytes(out)


ENCODERS = {'rgba5551': rgba5551, 'i4': i4}
