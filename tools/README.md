# Approved D2 pixel cat

`build-cat.py` contains the exact approved 32×32 D2 resting sprite as an integer
pixel array. It uses nine opaque colors plus transparency; the gold eye is on
the viewer's left and the blue eye on the right. The low ears, rounded cheeks,
long horizontal body, tucked paws and wrapped tail are preserved.

Rebuild with `python3 tools/build-cat.py` using Python 3 and Pillow. The four
SVGs have no runtime dependencies, scripts, linked images, gradients or filters.
The native cell runs are rendered with `crispEdges` at an integer ×12 scale.
Responsive browser scaling retains hard pixel edges.

The 24-second cycle mostly holds still. A blink changes six iris/lid cells into
two shallow three-cell closed-eye curves;
breathing lifts only the upper back by one native pixel; an occasional tail tip
moves one pixel. The head, tucked paws and ground contact stay fixed. There is
no stretch, toy, or full-body deformation. The first and last frames match the
approved sprite exactly.

The README uses native `picture` media queries for light/dark and reduced
motion and a native `details` control to fold the image away. Static companions
show the exact approved resting sprite. Animated SVGs also honor reduced motion
internally. Build-time checks cover the palette, binary alpha, connected anatomy,
fixed paws, exact loop reset, valid safe SVGs and nearest-neighbor round trips.
