# Pixel cat source

The cat shapes and motion are drawn specifically for this profile. No external artwork, scripts or embedded bitmap assets are loaded by the four SVGs.

To rebuild, run `python tools/build-cat.py` with Python 3 and Pillow installed. Pillow is used only to draw the original integer-cell masks while building; the resulting SVGs need no runtime dependencies.

The animation is a 30-second state cycle: rest, blink, attention, single-paw play, articulated stretch, curl, sleep and wake. The scene deliberately holds between actions. Discrete poses keep the pixel edges clear; nothing in the profile image is interactive.

`cat-light.svg` and `cat-dark.svg` animate. Their `-static.svg` companions are still images. The README chooses companions with native `<picture>` media queries and includes a native `<details>` control to hide the motion. An internal reduced-motion rule also keeps the default resting pose visible.
