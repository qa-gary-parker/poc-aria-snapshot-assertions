"""Shared manim helpers for narrated explainer scenes.

From yarstack (https://github.com/yarlson/yarstack); palette and fonts changed.
MIT License. Copyright (c) 2026 Yar Kravtsov. Permission is hereby granted, free of
charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions: The above copyright notice and
this permission notice shall be included in all copies or substantial portions of the
Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Copy this file next to the scene file. Each scene subclasses Narrated and wraps
the animations for beat i in `with self.beat(i):`. The beat plays its narration
clip and waits until the clip ends, so keep each beat's animations shorter than
its clip. Draw arrows with arrow() and animate them with grow_arrow(): manim's
Arrow and GrowArrow scale the tip and the line width with the arrow's length.
"""

import json
from contextlib import contextmanager
from pathlib import Path

from manim import (
    ORIGIN,
    RIGHT,
    AnimationGroup,
    Arrow,
    FadeOut,
    RoundedRectangle,
    Scene,
    Text,
    UpdateFromAlphaFunc,
    VGroup,
    config,
)

ROOT = Path(__file__).parent
AUDIO = ROOT / "audio"
BEAT_PAD = 0.45

BACKGROUND = "#0B0D0C"
PRIMARY = "#E6E8E3"
ACCENT = "#F2C94C"
GOOD = "#3FB950"
BAD = "#F85149"
NOTE = "#5CD0B3"
WARN = "#FF862F"
DIM = "#8A9088"
FONT = "IBM Plex Sans"
MONO = "JetBrains Mono"
ARROW_TIP = 0.22
ARROW_WIDTH = 4

config.background_color = BACKGROUND


def txt(s, size=28, color=PRIMARY, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def mono(s, size=22, color=PRIMARY):
    return Text(s, font=MONO, font_size=size, color=color)


def card(label, color=NOTE, w=1.25, h=0.62, size=24):
    box = RoundedRectangle(corner_radius=0.12, width=w, height=h, color=color, stroke_width=3)
    box.set_fill(color, opacity=0.12)
    return VGroup(box, txt(label, size, color)).arrange(ORIGIN)


def arrow(start, end, color=DIM, buff=0.12):
    return Arrow(
        start, end, buff=buff, color=color, stroke_width=ARROW_WIDTH, tip_length=ARROW_TIP,
        max_tip_length_to_length_ratio=1, max_stroke_width_to_length_ratio=1000,
    )


def grow_arrow(shape, **kwargs):
    start, end, color = shape.get_start(), shape.get_end(), shape.get_color()

    def extend(mob, alpha):
        mob.become(arrow(start, start + (end - start) * max(alpha, 0.01), color, buff=0))

    return UpdateFromAlphaFunc(shape, extend, **kwargs)


def flow(names, width=2.25, gap=0.22, color=DIM, size=20):
    boxes = VGroup(*[card(name, color, w=width, h=0.7, size=size) for name in names]).arrange(RIGHT, buff=gap)
    arrows = VGroup(*[arrow(boxes[i].get_right(), boxes[i + 1].get_left(), color, buff=0.03) for i in range(len(boxes) - 1)])
    return VGroup(boxes, arrows)


def light_up(stage, color=GOOD):
    box, label = stage
    return AnimationGroup(box.animate.set_color(color).set_fill(color, opacity=0.15), label.animate.set_color(color))


class Narrated(Scene):
    @contextmanager
    def beat(self, i):
        name = type(self).__name__
        clip = json.loads((AUDIO / "durations.json").read_text())[name][i]
        self.add_sound(str(AUDIO / clip["file"]))
        start = self.renderer.time
        yield
        remaining = clip["seconds"] + BEAT_PAD - (self.renderer.time - start)
        if remaining > 0:
            self.wait(remaining)

    def clear_all(self, run_time=0.6):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)

