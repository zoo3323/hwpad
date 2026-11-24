"""README 의 macOS 설치 영상(docs/images/install-mac.gif)을 그린다.

실제 화면 녹화가 아니라 장면을 그려 만든다(개인 화면이 찍히지 않게).
마지막 장면에는 앱 화면 캡처(docs/images/app.png)를 띄운다.

  uv run --with pillow python scripts/make-install-gif.py docs/images/app.png docs/images/install-mac.gif

ffmpeg 가 있으면 팔레트를 만들어 색 띠 없이 GIF 로 묶는다.
"""

import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

APP = "Hwpad"
REPO = "zoo3323/hwpad"
CMD = f"curl -fsSL https://raw.githubusercontent.com/{REPO}/main/install/install-mac.sh | bash"

S = 2  # 2배로 그려 줄여서 글자 가장자리를 부드럽게
W, H = 960 * S, 600 * S
NAVY = (30, 58, 138)

FONT_DIRS = [Path.home() / "Library/Fonts", Path("/Library/Fonts")]


def font(name, size, index=0):
    for d in FONT_DIRS:
        p = d / name
        if p.exists():
            return ImageFont.truetype(str(p), size * S, index=index)
    raise SystemExit(f"글꼴이 없습니다: {name}")


UI = lambda size: font("Pretendard-Medium.otf", size)
UI_BOLD = lambda size: font("Pretendard-Bold.otf", size)
MONO = lambda size: font("D2Coding-Ver1.3.2-20180524.ttc", size)


def background():
    img = Image.new("RGB", (W, H))
    top, bottom = (236, 238, 250), (247, 244, 246)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        row = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = row
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 26 * S), fill=(250, 250, 252))
    x = 14 * S
    for i, word in enumerate(["Finder", "파일", "편집", "보기", "이동", "윈도우", "도움말"]):
        f = UI_BOLD(12) if i == 0 else UI(12)
        d.text((x, 6 * S), word, font=f, fill=(20, 20, 20))
        x += d.textlength(word, font=f) + 18 * S
    return img


BG = None


def shadowed(canvas, box, radius, fill, blur=18, alpha=70, outline=None):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10 * S, x1, y1 + 10 * S), radius, fill=(20, 30, 60, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
    canvas.alpha_composite(sh)
    ImageDraw.Draw(canvas).rounded_rectangle(box, radius, fill=fill, outline=outline, width=S)


def caption(canvas, step, text):
    d = ImageDraw.Draw(canvas)
    f = UI_BOLD(19)
    tw = d.textlength(text, font=f)
    w = tw + 92 * S
    x0 = (W - w) / 2
    box = (x0, 520 * S, x0 + w, 574 * S)
    shadowed(canvas, box, 14 * S, NAVY + (255,), blur=10, alpha=60)
    cx, cy = x0 + 40 * S, 547 * S
    d.ellipse((cx - 15 * S, cy - 15 * S, cx + 15 * S, cy + 15 * S), fill="white")
    d.text((cx, cy), str(step), font=UI_BOLD(16), fill=NAVY, anchor="mm")
    d.text((x0 + 66 * S, cy), text, font=f, fill="white", anchor="lm")


def key_badge(canvas, text):
    d = ImageDraw.Draw(canvas)
    f = UI_BOLD(13)
    w = d.textlength(text, font=f) + 24 * S
    box = (W - 20 * S - w, 40 * S, W - 20 * S, 66 * S)
    shadowed(canvas, box, 8 * S, (255, 255, 255, 255), blur=6, alpha=40, outline=(220, 222, 230))
    d.text(((box[0] + box[2]) / 2, 53 * S), text, font=f, fill=(30, 30, 40), anchor="mm")


def spotlight(canvas, typed, cursor, result):
    d = ImageDraw.Draw(canvas)
    box = (300 * S, 150 * S, 660 * S, 194 * S)
    shadowed(canvas, box, 12 * S, (255, 255, 255, 245), blur=14, alpha=50, outline=(225, 228, 236))
    cx, cy = 322 * S, 172 * S
    d.ellipse((cx - 7 * S, cy - 8 * S, cx + 5 * S, cy + 4 * S), outline=(90, 90, 100), width=2 * S)
    d.line((cx + 3 * S, cy + 2 * S, cx + 9 * S, cy + 8 * S), fill=(90, 90, 100), width=2 * S)
    f = UI(19)
    tx = 342 * S
    if typed:
        d.text((tx, cy), typed, font=f, fill=(20, 20, 20), anchor="lm")
        tx += d.textlength(typed, font=f) + 3 * S
    else:
        d.text((tx + 6 * S, cy), "Spotlight 검색", font=f, fill=(170, 170, 178), anchor="lm")
    if cursor:
        d.line((tx, cy - 11 * S, tx, cy + 11 * S), fill=(40, 90, 220), width=2 * S)
    if result:
        rbox = (300 * S, 200 * S, 660 * S, 240 * S)
        shadowed(canvas, rbox, 10 * S, (255, 255, 255, 245), blur=10, alpha=40)
        d.rounded_rectangle((306 * S, 205 * S, 654 * S, 235 * S), 7 * S, fill=(37, 99, 235))
        d.rounded_rectangle((316 * S, 211 * S, 334 * S, 229 * S), 4 * S, fill=(30, 30, 30))
        d.text((320 * S, 220 * S), ">_", font=MONO(9), fill="white", anchor="lm")
        d.text((344 * S, 220 * S), "터미널", font=UI(15), fill="white", anchor="lm")


TERM = (60 * S, 70 * S, 900 * S, 468 * S)
TERM_FONT_SIZE = 16


def wrap(text, f, width, d):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    lines.append(cur)
    return lines


def terminal(canvas, rows, cursor=True, highlight=None, scale=1.0):
    """rows: [(text, kind)] kind = prompt|cmd|out|progress"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = TERM
    if scale != 1.0:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        hw, hh = (x1 - x0) / 2 * scale, (y1 - y0) / 2 * scale
        x0, y0, x1, y1 = cx - hw, cy - hh, cx + hw, cy + hh
    shadowed(layer, (x0, y0, x1, y1), 12 * S, (255, 255, 255, 255), blur=20, alpha=70, outline=(214, 216, 224))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x1, y0 + 34 * S), 12 * S, fill=(244, 244, 246))
    d.rectangle((x0, y0 + 20 * S, x1, y0 + 34 * S), fill=(244, 244, 246))
    d.line((x0, y0 + 34 * S, x1, y0 + 34 * S), fill=(222, 222, 228), width=S)
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = x0 + (19 + i * 20) * S
        d.ellipse((cx - 6 * S, y0 + 11 * S, cx + 6 * S, y0 + 23 * S), fill=c)
    d.text(((x0 + x1) / 2, y0 + 17 * S), "터미널 — zsh", font=UI(12), fill=(80, 80, 90), anchor="mm")
    if scale == 1.0:
        f = MONO(TERM_FONT_SIZE)
        lh = 26 * S
        y = y0 + 52 * S
        width = x1 - x0 - 40 * S
        last_end = None
        for text, kind in rows:
            if kind == "prompt":
                pre = "user@Mac ~ % "
                d.text((x0 + 20 * S, y), pre, font=f, fill=(110, 110, 125))
                px = x0 + 20 * S + d.textlength(pre, font=f)
                lines = wrap(text, f, x1 - 20 * S - px, d) if text else [""]
                for j, ln in enumerate(lines):
                    lx = px if j == 0 else x0 + 20 * S
                    if j > 0:
                        y += lh
                    if highlight and text:
                        tw = d.textlength(ln, font=f)
                        d.rectangle((lx - 2 * S, y - 3 * S, lx + tw + 2 * S, y + lh - 6 * S), fill=(205, 222, 255))
                    d.text((lx, y), ln, font=f, fill=(25, 25, 30))
                    last_end = (lx + d.textlength(ln, font=f), y)
            else:
                for ln in wrap(text, f, width, d):
                    d.text((x0 + 20 * S, y), ln, font=f, fill=(25, 25, 30))
                    last_end = (x0 + 20 * S + d.textlength(ln, font=f), y)
                    y += lh
                y -= lh
            y += lh
        if cursor and last_end:
            cx, cy = last_end
            d.rectangle((cx + 2 * S, cy + 1 * S, cx + 11 * S, cy + 20 * S), fill=(60, 60, 70))
    canvas.alpha_composite(layer)


def app_window(canvas, shot, t):
    """t: 0→1 떠오르는 정도"""
    ease = 1 - (1 - t) ** 3
    scale = 0.86 + 0.14 * ease
    tw = int(740 * S * scale)
    th = int(shot.height * tw / shot.width)
    img = shot.resize((tw, th), Image.LANCZOS)
    x = (W - tw) // 2
    y = int(36 * S + (1 - ease) * 30 * S)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.alpha_composite(img, (x, y))
    if ease < 1:
        a = layer.getchannel("A").point(lambda v: int(v * ease))
        layer.putalpha(a)
    canvas.alpha_composite(layer)


def crop_window(shot):
    """캡처 둘레의 그림자 여백을 덜어 창 둘레 조금만 남긴다."""
    bbox = shot.getchannel("A").point(lambda v: 255 if v > 200 else 0).getbbox()
    if not bbox:
        return shot
    pad = int(min(shot.size) * 0.02)
    x0, y0, x1, y1 = bbox
    return shot.crop((max(0, x0 - pad), max(0, y0 - pad), min(shot.width, x1 + pad), min(shot.height, y1 + pad)))


def build_frames(shot):
    frames = []  # (RGBA image, ms)

    def add(draw, ms=70, n=1):
        for _ in range(n):
            c = BG.copy().convert("RGBA")
            draw(c)
            frames.append((c, ms))

    s1 = '⌘ + 스페이스를 누르고 "터미널" 입력 → Enter'
    add(lambda c: caption(c, 1, s1), n=8)
    add(lambda c: (key_badge(c, "⌘ + 스페이스"), caption(c, 1, s1)), n=6)
    for blink in range(6):
        add(lambda c, b=blink: (spotlight(c, "", b % 2 == 0, False), caption(c, 1, s1)), n=2)
    for typed in ["ㅌ", "터", "터ㅁ", "터미", "터미ㄴ", "터미너", "터미널"]:
        add(lambda c, t=typed: (spotlight(c, t, True, False), caption(c, 1, s1)), n=2)
    add(lambda c: (spotlight(c, "터미널", True, True), caption(c, 1, s1)), n=8)
    add(lambda c: (key_badge(c, "Enter"), spotlight(c, "터미널", False, True), caption(c, 1, s1)), n=5)

    s2 = "아래 설치 줄을 붙여 넣고 Enter"
    for k in range(5):
        add(lambda c, k=k: (terminal(c, [], scale=0.9 + 0.025 * k), caption(c, 2, s2)))
    add(lambda c: (terminal(c, [("", "prompt")]), caption(c, 2, s2)), n=10)
    add(lambda c: (key_badge(c, "⌘ + V"), terminal(c, [(CMD, "prompt")], highlight=True), caption(c, 2, s2)), n=10)
    add(lambda c: (key_badge(c, "Enter"), terminal(c, [(CMD, "prompt")], cursor=False), caption(c, 2, s2)), n=5)
    head = [(CMD, "prompt"), (f"{APP}(Apple 칩)을 내려받는 중...", "out")]
    for p in [0, 3, 8, 15, 24, 35, 47, 58, 69, 79, 88, 95, 100]:
        bar = "#" * int(60 * p / 100)
        line = f"{bar:<60} {p:5.1f}%"
        add(lambda c, l=line: (terminal(c, head + [(l, "out")], cursor=False), caption(c, 2, s2)), n=2)
    done = head + [("#" * 60 + " 100.0%", "out"), (f"설치 완료: /Applications/{APP}.app", "out"), ("", "prompt")]
    add(lambda c: (terminal(c, done), caption(c, 2, s2)), n=14)

    s3 = f"{APP}가 경고 없이 바로 열립니다"
    for k in range(9):
        add(lambda c, t=(k + 1) / 9: (terminal(c, done, cursor=False), app_window(c, shot, t), caption(c, 3, s3)))
    add(lambda c: (terminal(c, done, cursor=False), app_window(c, shot, 1), caption(c, 3, s3)), ms=60, n=40)
    return frames


def main():
    global BG
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    shot = crop_window(Image.open(sys.argv[1]).convert("RGBA"))
    out = Path(sys.argv[2])
    BG = background()
    frames = build_frames(shot)
    small = [(f.convert("RGB").resize((W // S, H // S), Image.LANCZOS), ms) for f, ms in frames]
    if shutil.which("ffmpeg"):
        with tempfile.TemporaryDirectory() as tmp:
            concat = []
            for i, (f, ms) in enumerate(small):
                p = Path(tmp) / f"f{i:04d}.png"
                f.save(p)
                concat += [f"file '{p}'", f"duration {ms / 1000:.3f}"]
            concat.append(f"file '{Path(tmp) / f'f{len(small) - 1:04d}.png'}'")
            (Path(tmp) / "list.txt").write_text("\n".join(concat))
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(Path(tmp) / "list.txt"),
                 "-filter_complex", "[0:v]split[a][b];[a]palettegen=max_colors=192:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a",
                 "-loop", "0", str(out)],
                check=True,
            )
    else:
        imgs = [f for f, _ in small]
        imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=[ms for _, ms in small], loop=0, optimize=True)
    print(f"{out} ({len(small)}장, {sum(ms for _, ms in small) / 1000:.1f}초)")


if __name__ == "__main__":
    main()
