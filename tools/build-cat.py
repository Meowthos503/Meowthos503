"""Reproduce the approved D2 cat, cell for cell, with quiet native pixel motion.

Python 3 + Pillow are build-time tools only. SVGs have no runtime dependencies.
"""
from pathlib import Path
from collections import deque
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = 32
PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (21, 18, 31, 255),
    "s": (37, 32, 51, 255),
    "b": (56, 48, 68, 255),
    "m": (74, 62, 88, 255),
    "h": (102, 87, 116, 255),
    "p": (193, 125, 148, 255),
    "e": (121, 82, 108, 255),
    "g": (237, 189, 88, 255),
    "u": (102, 159, 198, 255),
}
# Exact approved D2-soft-cheek-loaf-32x32.png, without resampling or redrawing.
REST = (
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "....o.......o...................",
    "...obo.....obo..................",
    "...oebooooobeo..................",
    "...obbmmmmmbbo..................",
    "...obhhhhmmmmbo..ooooooo........",
    "...ommbbbbbbbbboomhhhhmmooo.....",
    "..obbbbbbbbbbbbbbbbbbbbbmmo.....",
    "..obbooobbooobbbbbbbbbbbbbbo.o..",
    "..obbggbbbuubbbbbbbbbbbbbbbbobo.",
    "..obbbbbbbbbbbbbbbbbbbbbbbbbbmo.",
    "...ommbbpbbbmmbbbbbbbbbboooobbo.",
    "...ossssosssssssssssssooosmmbo..",
    "....ossososbooooooobmmmmmmmoo...",
    "....oooooooo.......oooooooo.....",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
)


def image(rows):
    assert len(rows) == SIZE and all(len(row) == SIZE for row in rows)
    out = Image.new("RGBA", (SIZE, SIZE))
    out.putdata([PALETTE[p] for row in rows for p in row])
    return out


def pixels(im):
    return [im.getpixel((x, y)) for y in range(SIZE) for x in range(SIZE)]


def frame(close=False, breathe=False, tail=False):
    rows = [list(row) for row in REST]
    if close:
        # A shallow three-cell curve replaces each iris/lid cluster. The
        # approved open-eye sprite is unchanged; closed eyes aren't dark holes.
        for x in (5, 6, 10, 11):
            rows[20][x] = "b"
        for x in (6, 11):
            rows[19][x] = "b"
            rows[20][x] = "o"
    if breathe:
        # Only the upper back lifts by one native cell. Head, shoulder contact,
        # tucked paws, belly and wrapped lower tail are fixed.
        for x in range(16, 26):
            for y in range(14, 18):
                rows[y][x] = REST[y + 1][x]
    if tail:
        # A single outline tip shifts one cell right, still attached to the tail.
        rows[19][29] = "."
        rows[19][30] = "o"
    return image(rows)


FRAMES = {
    "rest": frame(),
    "breathe": frame(breathe=True),
    "closed": frame(close=True),
    "closed-breathe": frame(close=True, breathe=True),
    "tail": frame(tail=True),
}
DURATION = 24.0
# Mostly still holds. The first and last state are exactly the approved rest.
TIMELINE = [
    (0.0, "rest"),
    (3.2, "breathe"), (4.6, "rest"),
    (6.8, "closed"), (6.98, "rest"),
    (10.8, "tail"), (11.15, "rest"),
    (14.0, "closed"),
    (16.0, "closed-breathe"), (17.2, "closed"),
    (18.6, "rest"),
    (21.6, "breathe"), (22.8, "rest"),
    (DURATION, "rest"),
]
THEMES = {"light": "#eee9ef", "dark": "#51435d"}


def state(t):
    selected = "rest"
    for start, name in TIMELINE:
        if start <= t:
            selected = name
    return selected


def shapes(im):
    """Encode each native horizontal color run as integer-coordinate cells."""
    colors = {}
    for y in range(SIZE):
        x = 0
        while x < SIZE:
            color = im.getpixel((x, y))
            if not color[3]:
                x += 1
                continue
            end = x + 1
            while end < SIZE and im.getpixel((end, y)) == color:
                end += 1
            key = "#%02x%02x%02x" % color[:3]
            colors.setdefault(key, []).append(f"M{x} {y}h{end-x}v1h-{end-x}Z")
            x = end
    return "".join(f'<path fill="{color}" d="{"".join(runs)}"/>'
                   for color, runs in colors.items())


def css():
    rules = []
    for name in FRAMES:
        keys = []
        previous = None
        for t, selected in TIMELINE:
            visible = int(selected == name)
            if visible != previous or t == DURATION:
                keys.append(f"{100*t/DURATION:.8f}%{{opacity:{visible}}}")
                previous = visible
        rules.append(f"@keyframes frame-{name}{{{''.join(keys)}}}"
                     f".frame-{name}{{animation:frame-{name} {DURATION:g}s steps(1,end) infinite}}")
    rules.append("@media(prefers-reduced-motion:reduce){"
                 ".cat-frame{animation:none!important;opacity:0!important}"
                 ".frame-rest{opacity:1!important}}")
    return "\n".join(rules)


def svg(theme="light", motion=True, t=None):
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" width="900" height="300" role="img" aria-labelledby="cat-title cat-desc">',
        '<title id="cat-title">Meowthos · 困困小猫</title>',
        '<desc id="cat-desc">Original 32-by-32 charcoal pixel cat: a low, long loaf with short ears, tucked paws, a wrapped tail, a gold left eye and blue right eye. It rests, blinks, breathes gently and dozes in a quiet 24-second loop. The surrounding fold control hides the image; reduced motion shows the exact resting sprite.</desc>',
    ]
    if motion and t is None:
        out += ['<style>', css(), '</style>']
    out += ['<g shape-rendering="crispEdges">',
            f'<path fill="{THEMES[theme]}" d="M0 0H900V300H0Z"/>',
            '<g transform="translate(258 -45) scale(12)">']
    selected = state(0 if t is None else t)
    for name, im in FRAMES.items():
        if t is not None or not motion:
            if name == selected:
                out.append(shapes(im))
        else:
            out.append(f'<g class="cat-frame frame-{name}" opacity="{int(name == "rest")}">{shapes(im)}</g>')
    out += ['</g>', '</g>', '</svg>']
    return "\n".join(out) + "\n"


def scene(theme, name="rest"):
    out = Image.new("RGB", (900, 300), THEMES[theme])
    sprite = FRAMES[name].resize((384, 384), Image.Resampling.NEAREST)
    out.paste(sprite, (258, -45), sprite)
    return out


def connected(im):
    cells = {(x, y) for y in range(SIZE) for x in range(SIZE)
             if im.getpixel((x, y))[3]}
    unseen = set(cells)
    todo = deque([unseen.pop()])
    while todo:
        x, y = todo.popleft()
        for neighbor in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if neighbor in unseen:
                unseen.remove(neighbor)
                todo.append(neighbor)
    return not unseen


def validate():
    rest = image(REST)
    assert hashlib.sha256(rest.tobytes()).hexdigest() == '6af24de15d050a4e91b99aa89b2fe601ca7c72e64659259b99bdc8fef5857c46'
    details = {}
    palette = set(PALETTE.values())
    for name, im in FRAMES.items():
        assert im.size == (32, 32)
        assert set(pixels(im)) <= palette
        assert {c[3] for c in pixels(im)} == {0, 255}
        assert connected(im), name
        changed = [(x, y) for y in range(SIZE) for x in range(SIZE)
                   if im.getpixel((x, y)) != rest.getpixel((x, y))]
        if name not in ("closed", "closed-breathe"):
            assert im.crop((0, 0, 15, 32)).tobytes() == rest.crop((0, 0, 15, 32)).tobytes()
        else:
            assert all((x >= 16 and y < 18) or (y == 20 and x in (5, 6, 10, 11)) or (y == 19 and x in (6, 11))
                       for x, y in changed)
        assert im.crop((0, 22, 32, 32)).tobytes() == rest.crop((0, 22, 32, 32)).tobytes()
        nearest = im.resize((384, 384), Image.Resampling.NEAREST)
        assert nearest.resize((32, 32), Image.Resampling.NEAREST).tobytes() == im.tobytes()
        details[name] = {"native_size": [32, 32], "changed_cells": len(changed),
                         "opaque_colors": len({c for c in pixels(im) if c[3]}),
                         "alpha_values": [0, 255], "four_connected": True,
                         "tucked_paws_and_floor_unchanged": True,
                         "rgba_sha256": hashlib.sha256(im.tobytes()).hexdigest()}
    assert FRAMES[state(0)].tobytes() == FRAMES[state(DURATION)].tobytes() == rest.tobytes()
    assert all(TIMELINE[i][0] < TIMELINE[i+1][0] for i in range(len(TIMELINE)-1))
    for theme in THEMES:
        for motion in (True, False):
            doc = svg(theme, motion)
            root = ET.fromstring(doc)
            for el in root.iter():
                assert el.tag.split('}')[-1] not in ("script", "image", "foreignObject", "use", "linearGradient", "radialGradient", "filter")
                assert not any(k.startswith("on") or k.endswith("href") for k in el.attrib)
            assert 'scale(12)' in doc and 'shape-rendering="crispEdges"' in doc
            if not motion:
                assert "<style>" not in doc and "cat-frame" not in doc
    return {"duration_seconds": DURATION, "timeline": TIMELINE,
            "first_and_last_exact_rest": True,
            "rest_opaque_palette": ["#%02x%02x%02x" % c[:3] for c in PALETTE.values() if c[3]],
            "frames": details}


def review_artifacts(proof):
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    try:
        fontpath = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
        font = ImageFont.truetype(fontpath, 18)
        small = ImageFont.truetype(fontpath, 13)
    except OSError:
        font = ImageFont.load_default(size=18)
        small = ImageFont.load_default(size=13)
    contact = Image.new("RGB", (1260, 414), "#eee9ef")
    draw = ImageDraw.Draw(contact)
    draw.text((22, 12), "D2 · 原生 32×32 · 同一只猫的五个微小状态", font=font, fill="#292432")
    labels = {"rest": "批准原帧 · 完全一致", "breathe": "背部一像素呼吸", "closed": "闭眼 · 三格浅浅眼睑", "closed-breathe": "闭眼时轻轻呼吸", "tail": "尾尖偶尔移一像素"}
    for i, (name, im) in enumerate(FRAMES.items()):
        x = 20 + i * 248
        sprite = im.resize((224, 224), Image.Resampling.NEAREST)
        contact.paste(sprite, (x, 58), sprite)
        draw.text((x, 298), labels[name], font=small, fill="#292432")
        draw.text((x, 323), f"与原帧差 {proof['frames'][name]['changed_cells']} 格", font=small, fill="#766b80")
        im.save(qa / (name + '-32x32.png'))
    draw.text((22, 369), "24 秒慢循环：歇着 → 眨眼 → 尾尖轻动 → 打盹 → 睁眼 · 每个像素格都是整数坐标", font=small, fill="#766b80")
    contact.save(qa / 'Meowthos-D2-animation-contact-sheet.png')
    scenes = [scene('light', name) for _, name in TIMELINE[:-1]]
    durations = [round(1000*(TIMELINE[i+1][0]-TIMELINE[i][0])) for i in range(len(TIMELINE)-1)]
    scenes[0].save(qa / 'Meowthos-D2-quiet-loop.gif', save_all=True,
                   append_images=scenes[1:], duration=durations, loop=0,
                   optimize=False, disposal=1)
    for theme in THEMES:
        scene(theme).save(qa / f'hero-{theme}-exact-rest.png')
    (qa / 'pixel-proof.json').write_text(json.dumps(proof, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    (ROOT / 'assets').mkdir(exist_ok=True)
    proof = validate()
    for theme in THEMES:
        for motion in (True, False):
            name = 'cat-' + theme + ('' if motion else '-static') + '.svg'
            (ROOT / 'assets' / name).write_text(svg(theme, motion), encoding='utf-8')
    review_artifacts(proof)
    print(json.dumps(proof, indent=2, ensure_ascii=False))
