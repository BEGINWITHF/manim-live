"""Determine ffmpeg's BMP orientation handling empirically.
Renders RED square on TOP half, BLUE on BOTTOM half, reads back the
framebuffer, writes the SAME rows with positive and negative biHeight,
then decodes both with ffmpeg and PIL and reports where RED lands."""
import ctypes
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from manim import Scene, Square, Circle, UP, DOWN
from real_time_manim.vulkan_bind import MLWindow

def main():
    render = MLWindow(1280, 720)
    scene = Scene()
    render.scene = scene
    sq = Square(side_length=2.0, color="#FF0000")
    sq.set_fill("#FF0000", opacity=1.0)
    sq.shift(UP * 2)
    cr = Circle(radius=1.5, color="#0000FF")
    cr.set_fill("#0000FF", opacity=1.0)
    cr.shift(DOWN * 2)
    scene.add(sq, cr)
    for _ in range(30):
        if not render.tick():
            break
        render.sync(scene, 0.0)

    w = ctypes.c_int(0); h = ctypes.c_int(0)
    buf = (ctypes.c_ubyte * (4 * 4096 * 4096))()
    dll = render.dll
    dll.Vulkan_ReadPixels.restype = ctypes.c_int
    dll.Vulkan_ReadPixels.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                                      ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
    dll.Vulkan_ReadPixels(buf, ctypes.byref(w), ctypes.byref(h))
    render.tick(); render.sync(scene, 0.0)
    rc = dll.Vulkan_ReadPixels(buf, ctypes.byref(w), ctypes.byref(h))
    print(f"readback rc={rc} {w.value}x{h.value}")
    render.close()
    assert rc == 1

    W, H = w.value, h.value
    arr = np.frombuffer(buf, dtype=np.uint8, count=W * H * 4).reshape(H, W, 4)
    bgr = np.ascontiguousarray(arr[:, :, :3][:, :, ::-1])  # RGBA -> BGR
    row_bytes = ((W * 3 + 3) // 4) * 4

    def write_bmp(path, bi_height):
        with open(path, "wb") as f:
            header = bytearray(54)
            header[0:2] = b"BM"
            header[2:6] = (54 + row_bytes * H).to_bytes(4, "little")
            header[10:14] = (54).to_bytes(4, "little")
            header[14:18] = (40).to_bytes(4, "little")
            header[18:22] = W.to_bytes(4, "little")
            header[22:26] = bi_height.to_bytes(4, "little", signed=True)
            header[26:28] = (1).to_bytes(2, "little")
            header[28:30] = (24).to_bytes(2, "little")
            header[34:38] = (row_bytes * H).to_bytes(4, "little")
            f.write(header)
            for y in range(H):  # rows in buffer order (row 0 = TOP of image)
                f.write(bgr[y].tobytes())
                f.write(b"\x00" * (row_bytes - W * 3))

    tmp = tempfile.mkdtemp(prefix="bmp_probe_")
    pos_bmp = os.path.join(tmp, "pos.bmp")
    neg_bmp = os.path.join(tmp, "neg.bmp")
    write_bmp(pos_bmp, H)    # positive biHeight (bottom-up per spec)
    write_bmp(neg_bmp, -H)   # negative biHeight (top-down per spec)

    def decode_pil(p):
        from PIL import Image
        img = Image.open(p).convert("RGB")
        a = np.asarray(img)
        return a.shape, tuple(a[a.shape[0] // 4, a.shape[1] // 2]), tuple(a[3 * a.shape[0] // 4, a.shape[1] // 2])

    def decode_ffmpeg(p, tag):
        out = os.path.join(tmp, f"{tag}_out.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, out], check=True)
        from PIL import Image
        a = np.asarray(Image.open(out).convert("RGB"))
        return a.shape, tuple(a[a.shape[0] // 4, a.shape[1] // 2]), tuple(a[3 * a.shape[0] // 4, a.shape[1] // 2])

    for name, p in (("positive", pos_bmp), ("negative", neg_bmp)):
        shape, top, bottom = decode_pil(p)
        print(f"PIL     {name:8s} {shape} top_quarter={top} bottom_quarter={bottom}")
        shape, top, bottom = decode_ffmpeg(p, name)
        print(f"FFMPEG  {name:8s} {shape} top_quarter={top} bottom_quarter={bottom}")

    print(f"\nRED=(255,0,0) at TOP, BLUE=(0,0,255) at BOTTOM is CORRECT.")
    print(f"tmp dir: {tmp}")

if __name__ == "__main__":
    main()
