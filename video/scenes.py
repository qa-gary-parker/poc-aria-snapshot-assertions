from manim import *
from scenekit import *

LINE = "#2E332F"
SUITES = ["CSS selectors", "test IDs", "role locators", "ARIA snapshots"]
REGRESSIONS = ["heading", "list", "button", "alert", "label"]
CAUGHT = {
    "CSS selectors": [0, 1, 0, 0, 0],
    "test IDs": [0, 0, 0, 0, 0],
    "role locators": [0, 1, 1, 1, 1],
    "ARIA snapshots": [1, 1, 1, 1, 1],
}
DRIFT_V2 = {"CSS selectors": 0, "test IDs": 6, "role locators": 5, "ARIA snapshots": 3}


def code(s, size=22, color=PRIMARY, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def xspan(mob, s, sub):
    """Left and right x of `sub` inside a one-line monospace Text built from `s`."""
    i, w = s.index(sub), mob.width / len(s)
    left = mob.get_left()[0]
    return left + i * w, left + (i + len(sub)) * w


def underline(mob, s, sub, color):
    x0, x1 = xspan(mob, s, sub)
    y = mob.get_bottom()[1] - 0.08
    return Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=4)


def cell(w=1.3, h=0.56):
    box = RoundedRectangle(corner_radius=0.08, width=w, height=h, color=LINE, stroke_width=2)
    box.set_fill(LINE, opacity=0.35)
    return box


def mark(box, caught):
    color = GOOD if caught else BAD
    label = code("caught" if caught else "miss", 17, color).move_to(box)
    return AnimationGroup(box.animate.set_stroke(color).set_fill(color, opacity=0.16), FadeIn(label)), label


def total_color(n):
    return GOOD if n == 5 else BAD if n <= 1 else PRIMARY


def matrix():
    header = VGroup(*[code(r, 17, DIM) for r in REGRESSIONS])
    rows = VGroup()
    for suite in SUITES:
        label = txt(suite, 26)
        cells = VGroup(*[cell(1.4, 0.6) for _ in REGRESSIONS]).arrange(RIGHT, buff=0.14)
        rows.add(VGroup(label, cells))
    rows.arrange(DOWN, buff=0.32)
    for row in rows:
        row[0].move_to([-5.8, row.get_y(), 0], aligned_edge=LEFT)
        row[1].move_to([1.0, row.get_y(), 0])
    for h, c in zip(header, rows[0][1]):
        h.next_to(c, UP, buff=0.22)
    return VGroup(header, rows)


def app_wire(scale=1.0):
    frame = RoundedRectangle(corner_radius=0.1, width=4.8, height=4.4, color=LINE, stroke_width=3)
    bar = code("TaskBoard", 18, DIM).next_to(frame.get_top(), DOWN, buff=0.2).align_to(frame, LEFT).shift(RIGHT * 0.3)
    heading = Text("My Tasks", font=FONT, font_size=34, weight=BOLD, color=PRIMARY).next_to(bar, DOWN, buff=0.3, aligned_edge=LEFT)
    count = txt("2 active", 18, DIM).next_to(heading, DOWN, buff=0.12, aligned_edge=LEFT)
    field = RoundedRectangle(corner_radius=0.06, width=2.9, height=0.45, color=DIM, stroke_width=2)
    field.next_to(count, DOWN, buff=0.25, aligned_edge=LEFT)
    hint = txt("New task", 16, DIM).move_to(field).align_to(field, LEFT).shift(RIGHT * 0.15)
    add = VGroup(RoundedRectangle(corner_radius=0.06, width=0.9, height=0.45, color=PRIMARY, stroke_width=2), txt("Add", 16))
    add[1].move_to(add[0])
    add.next_to(field, RIGHT, buff=0.15)
    items = VGroup()
    for name, done in [("Write report", True), ("Review PR", True), ("Ship release", False)]:
        row = VGroup(txt(name, 18))
        if done:
            btn = VGroup(RoundedRectangle(corner_radius=0.05, width=0.8, height=0.34, color=DIM, stroke_width=2), txt("Done", 14, DIM))
            btn[1].move_to(btn[0])
            btn.move_to(row[0]).shift(RIGHT * 2.6).align_to(row[0], DOWN).shift(DOWN * 0.05)
            row.add(btn)
        items.add(row)
    items.arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(field, DOWN, buff=0.35, aligned_edge=LEFT)
    for row in items:
        if len(row) > 1:
            row[1].set_x(frame.get_right()[0] - 0.75)
    return VGroup(frame, bar, heading, count, field, hint, add, items).scale(scale)


def indented(lines, size=24, color=PRIMARY):
    """Monospace block that keeps leading indentation (Text drops leading spaces)."""
    cw = code("M" * 20, size).width / 20
    mobs = VGroup(*[code(t.lstrip(), size, color) for t in lines]).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    for mob, t in zip(mobs, lines):
        mob.shift(RIGHT * cw * (len(t) - len(t.lstrip())))
    return mobs


def terminal(lines, width=None):
    texts = VGroup(*lines).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    width = max(width or 0, texts.width + 0.8)
    box = RoundedRectangle(corner_radius=0.12, width=width, height=texts.height + 0.8, color=LINE, stroke_width=3)
    box.set_fill(LINE, opacity=0.3)
    texts.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.4)
    return VGroup(box, texts)


def prompt(cmd, size=22):
    return code(f"$ {cmd}", size, PRIMARY, t2c={"$": DIM})


def fill_row(row, suite, run_time=1.2):
    anims, labels = zip(*[mark(c, x) for c, x in zip(row[1], CAUGHT[suite])])
    n = sum(CAUGHT[suite])
    total = code(f"{n}/5", 26, total_color(n)).next_to(row[1], RIGHT, buff=0.4)
    return AnimationGroup(LaggedStart(*anims, lag_ratio=0.1), FadeIn(total), run_time=run_time), VGroup(*labels, total)


class S1Result(Timed):
    def construct(self):
        title = code("5 seeded accessibility regressions  ×  4 suites", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        header, rows = matrix()
        self.at("five accessibility regressions")
        self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.15) for h in header], lag_ratio=0.15), run_time=0.9)
        self.at("four test suites")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.15), run_time=0.9)
        ids_fill, ids_labels = fill_row(rows[1], "test IDs")
        green = code("7/7 green", 18, GOOD).next_to(ids_labels[-1], DOWN, buff=0.08, aligned_edge=LEFT)
        self.at("caught none")
        self.play(ids_fill)
        self.at("every test stayed green")
        self.play(FadeIn(green, shift=UP * 0.1), run_time=0.5)
        aria_fill, _ = fill_row(rows[3], "ARIA snapshots")
        self.at("caught all five")
        self.play(aria_fill)

        best = txt("survives change best", 30)
        dot = txt("·", 30, DIM)
        least = txt("notices least", 30, BAD)
        VGroup(best, dot, least).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.8)
        self.at("survives change best")
        self.play(rows[0].animate.set_opacity(0.3), rows[2].animate.set_opacity(0.3), FadeIn(best, shift=UP * 0.2), run_time=0.7)
        self.at("notices least")
        self.play(FadeIn(VGroup(dot, least), shift=UP * 0.2), Indicate(rows[1][0], color=BAD, scale_factor=1.08), run_time=0.8)
        self.at("here is why")
        self.play(self.camera_to(13.4, [0.3, -0.3, 0]), run_time=1.2, rate_func=smooth)
        self.end()


class S2Setup(Timed):
    def construct(self):
        self.add(code("the testbed", 22, DIM).to_edge(UP, buff=0.7))
        app = app_wire(0.95).move_to([-3.6, 0.2, 0])
        scenarios = code("7 scenarios", 20, DIM).next_to(app, DOWN, buff=0.3)
        self.at("small task board app")
        self.play(FadeIn(app, lag_ratio=0.1), run_time=1.2)
        self.at("seven user scenarios")
        self.play(FadeIn(scenarios, shift=UP * 0.1), run_time=0.5)
        samples = [
            ("CSS selectors", 'locator("#dashboard-title")'),
            ("test IDs", 'getByTestId("dashboard-title")'),
            ("role locators", 'getByRole("heading", { name: "My Tasks" })'),
            ("ARIA snapshots", "toMatchAriaSnapshot(`…`)"),
        ]
        cards = VGroup(*[VGroup(txt(name, 26, DIM), code(sample, 17, DIM)).arrange(DOWN, buff=0.12, aligned_edge=LEFT) for name, sample in samples])
        cards.arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to([3.3, 0.2, 0])
        self.at("four ways")
        self.play(LaggedStart(*[FadeIn(c[0], shift=LEFT * 0.2) for c in cards], lag_ratio=0.2), run_time=0.8)
        for phrase, card in zip(["css selectors", "test id", "role locators", "and aria snapshots"], cards):
            self.at(phrase)
            self.play(card[0].animate.set_color(PRIMARY), FadeIn(card[1], shift=LEFT * 0.15), run_time=0.5)

        template = [
            '- heading "My Tasks" [level=2]',
            "- text: 2 active",
            '- textbox "New task"',
            '- button "Add"',
        ]
        block = terminal([code(line, 22) for line in template])
        ref = code("tests/aria-snapshots.spec.ts:29", 16, DIM)
        self.at("the snapshot suite acts")
        self.play(FadeOut(VGroup(cards[0], cards[1], scenarios)), app.animate.set_opacity(0.35), cards[2].animate.set_opacity(0.6), run_time=0.7)
        self.at("but every assertion")
        self.play(FadeOut(cards[2]), cards[3].animate.move_to([-0.6, 2.4, 0], aligned_edge=LEFT), run_time=0.7, rate_func=smooth)
        block.next_to(cards[3], DOWN, buff=0.35).align_to(cards[3], LEFT)
        ref.next_to(block, DOWN, buff=0.18).align_to(block, LEFT)
        self.at("short template")
        self.play(FadeIn(block[0]), LaggedStart(*[FadeIn(t, shift=RIGHT * 0.15) for t in block[1]], lag_ratio=0.3), run_time=1.4)
        self.play(FadeIn(ref), run_time=0.4)
        self.end()


class S3Regressions(Timed):
    def construct(self):
        builds = ["r1-heading", "r2-list", "r3-button", "r4-alert", "r5-label"]
        changes = [
            ("<h2>My Tasks</h2>", "<h4>My Tasks</h4>"),
            ("<ul><li>", "<div><div>"),
            ("<button>Active</button>", "<div>Active</div>"),
            ('<div role="alert">', "<div>"),
            ('<label for="username">', '<label for="user">'),
        ]
        names = VGroup(*[code(b, 22, ACCENT) for b in builds]).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([-4.6, -0.2, 0])
        title = code("v1  +  one regression per build", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        self.at("five regressions")
        self.play(LaggedStart(*[FadeIn(n, shift=RIGHT * 0.2) for n in names], lag_ratio=0.2), run_time=1.2)
        rows = VGroup()
        for name, (before, after) in zip(names, changes):
            b = code(before, 20, DIM).move_to([-2.8, name.get_y(), 0], aligned_edge=LEFT)
            arr = arrow([1.3, name.get_y(), 0], [2.0, name.get_y(), 0], DIM)
            a = code(after, 20, ACCENT).move_to([2.25, name.get_y(), 0], aligned_edge=LEFT)
            rows.add(VGroup(b, arr, a))
        for phrase, row in zip(["a heading drops", "a list becomes", "a button becomes", "an alert loses", "a label loses"], rows):
            self.at(phrase)
            self.play(FadeIn(row[0]), grow_arrow(row[1]), FadeIn(row[2], shift=RIGHT * 0.15), run_time=0.7)

        left = app_wire(0.62)
        right = app_wire(0.62)
        pair = VGroup(left, right).arrange(RIGHT, buff=1.2).move_to([0, 0.75, 0])
        tags = VGroup(code("v1", 18, DIM).next_to(left, UP, buff=0.15), code("r1-heading", 18, ACCENT).next_to(right, UP, buff=0.15))
        same = txt("on screen: identical", 24, DIM).next_to(pair, DOWN, buff=0.3)
        tree = VGroup(
            VGroup(code("v1", 20, DIM), code('heading "My Tasks" [level=2]', 20, DIM)),
            VGroup(code("r1-heading", 20, ACCENT), code('heading "My Tasks" [level=4]', 20, PRIMARY, t2c={"[level=4]": ACCENT})),
        )
        for row in tree:
            row[1].next_to(row[0], RIGHT, buff=0.4)
        tree.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        for row in tree:
            row[1].set_x(tree[1][1].get_x())
        tree.next_to(same, DOWN, buff=0.35)
        changed = txt("accessibility tree: changed", 24, ACCENT).next_to(tree, DOWN, buff=0.3)
        self.at("on screen every build")
        self.play(
            FadeOut(VGroup(rows, *names[1:], title), shift=UP * 0.3),
            ReplacementTransform(names[0], tags[1]),
            FadeIn(pair), FadeIn(tags[0]),
            run_time=0.9, rate_func=smooth,
        )
        self.at("looks the same")
        self.play(FadeIn(same, shift=UP * 0.1), run_time=0.5)
        self.at("only the accessibility tree")
        self.play(FadeIn(tree, shift=UP * 0.15), FadeIn(changed), run_time=0.8)
        self.end()


class S4Blind(Timed):
    def construct(self):
        html = '<h4 data-testid="dashboard-title">My Tasks</h4>'
        markup = code(html, 26, PRIMARY, t2c={"h4": ACCENT}).move_to([0, 0.6, 0])
        locator = code('getByTestId("dashboard-title")', 26).move_to([0, 2.4, 0])
        x0, x1 = xspan(markup, html, 'data-testid="dashboard-title"')
        link = arrow(locator.get_bottom(), [(x0 + x1) / 2, markup.get_top()[1], 0], DIM)
        attr = underline(markup, html, 'data-testid="dashboard-title"', DIM)
        note = txt("private attribute: unchanged", 22, DIM).next_to(markup, DOWN, buff=0.35)
        note.set_x((x0 + x1) / 2)
        self.at("the test id suite finds")
        self.play(FadeIn(locator, shift=DOWN * 0.15), run_time=0.6)
        self.at("private attribute")
        self.play(FadeIn(markup), Create(attr), run_time=0.8)
        self.at("the demoted heading")
        self.play(FadeIn(note, shift=UP * 0.1), Indicate(markup[1:3], color=ACCENT), run_time=0.8)
        self.at("the locator still matches")
        self.play(grow_arrow(link), run_time=0.6)
        check = code('toHaveText("My Tasks")', 24).move_to([-1.5, -1.4, 0])
        result = code("✓ logs in and shows the dashboard", 22, DIM).next_to(check, DOWN, buff=0.35, aligned_edge=LEFT)
        missed = txt("regression missed", 24, BAD).next_to(result, RIGHT, buff=0.5)
        self.at("still says my tasks")
        self.play(FadeIn(check, shift=UP * 0.1), run_time=0.6)
        self.at("the test passes")
        self.play(FadeIn(result), FadeIn(missed, shift=LEFT * 0.2), run_time=0.7)

        build = code("app/v1-regressed  ·  all 5 regressions in one build", 20, ACCENT).move_to([0, 2.0, 0])
        term = terminal([
            prompt("APP_VERSION=v1-regressed npx playwright test test-ids"),
            code("7 passed (2.6s)", 22, GOOD),
        ]).move_to([0, 0.4, 0])
        verdict = txt("5 regressions in this build  ·  0 caught", 30, BAD).next_to(term, DOWN, buff=0.6)
        self.at("with all five regressions")
        self.play(
            FadeOut(VGroup(markup, attr, note, link, check, result, missed), shift=DOWN * 0.3),
            ReplacementTransform(locator, build),
            FadeIn(term[0]), FadeIn(term[1][0]),
            run_time=0.9, rate_func=smooth,
        )
        self.at("seven of seven green")
        self.play(FadeIn(term[1][1], shift=UP * 0.1), run_time=0.5)
        self.at("never looks at what users get")
        self.play(FadeIn(verdict, shift=UP * 0.2), run_time=0.8)
        self.end()


class S5Caught(Timed):
    def construct(self):
        line = '- heading "My Tasks" [level=2]'
        template = code(line, 34).move_to([0, 1.8, 0])
        role = underline(template, line, "heading", PRIMARY)
        level = underline(template, line, "[level=2]", PRIMARY)
        labels = VGroup(
            code("role", 18, DIM).next_to(role, DOWN, buff=0.15),
            code("level", 18, DIM).next_to(level, DOWN, buff=0.15),
        )
        self.at("the snapshot template")
        self.play(FadeIn(template, shift=DOWN * 0.15), run_time=0.7)
        self.at("the role")
        self.play(Create(role), FadeIn(labels[0]), run_time=0.6)
        self.at("heading level")
        self.play(Create(level), FadeIn(labels[1]), run_time=0.6)
        error = code("Error: expect(locator).toMatchAriaSnapshot(expected) failed", 18, DIM)
        expected = VGroup(code("expected", 18, DIM), code('- heading "My Tasks" [level=2]', 24, DIM)).arrange(RIGHT, buff=0.5)
        received = VGroup(code("received", 18, DIM), code('- heading "My Tasks" [level=4]', 24, PRIMARY, t2c={"[level=4]": ACCENT})).arrange(RIGHT, buff=0.5)
        diff = terminal([error, expected, received], width=11.0).move_to([0, -0.9, 0])
        caught = txt("test failed  =  regression caught", 26, GOOD).next_to(diff, DOWN, buff=0.4)
        self.at("expected level two")
        self.play(FadeIn(diff[0]), FadeIn(error), FadeIn(expected, shift=UP * 0.1), run_time=0.7)
        self.at("received level four")
        self.play(FadeIn(received, shift=UP * 0.1), run_time=0.6)
        self.at("the test fails")
        self.play(FadeIn(caught, shift=UP * 0.2), run_time=0.7)

        query = code('getByRole("heading", { name: "My Tasks" })', 28).move_to([0, 1.6, 0])
        targets = VGroup(code("<h2>My Tasks</h2>", 24, DIM), code("<h4>My Tasks</h4>", 24, PRIMARY, t2c={"h4": ACCENT})).arrange(RIGHT, buff=2.4).move_to([0, -0.4, 0])
        links = VGroup(*[arrow(query.get_bottom(), t.get_top(), DIM) for t in targets])
        both = VGroup(*[code("matches", 18, DIM).next_to(t, DOWN, buff=0.2) for t in targets])
        missed = txt("role locators: missed", 26, BAD).next_to(targets, DOWN, buff=1.0)
        self.at("a role locator")
        self.play(FadeOut(VGroup(template, role, level, labels, diff, caught), shift=UP * 0.4), FadeIn(query, shift=UP * 0.2), run_time=0.8, rate_func=smooth)
        self.at("matches a level four")
        self.play(FadeIn(targets), *[grow_arrow(a) for a in links], run_time=0.8)
        self.play(FadeIn(both), run_time=0.4)
        self.at("missed this one")
        self.play(FadeIn(missed, shift=UP * 0.2), run_time=0.6)

        header, rows = matrix()
        self.at("final count")
        self.play(FadeOut(VGroup(query, targets, links, both, missed), shift=UP * 0.4), FadeIn(header), FadeIn(rows), run_time=0.8)
        for phrase, row, suite in zip(["css selectors caught", "test id caught", "role locators caught", "aria snapshots caught"], rows, SUITES):
            self.at(phrase)
            anim, _ = fill_row(row, suite, 0.9)
            self.play(anim)
        self.end()


class S6Cost(Timed):
    def construct(self):
        title = VGroup(
            code("separate drift run  ·  no seeded regressions", 18, DIM),
            code("suites written for v1, run on the v2 redesign  ·  7 tests", 22, DIM),
        ).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.5)
        self.add(title)
        rows = VGroup()
        for suite in SUITES:
            passed = DRIFT_V2[suite]
            squares = VGroup(*[cell(0.62, 0.48) for _ in range(7)]).arrange(RIGHT, buff=0.1)
            for i, sq in enumerate(squares):
                color = GOOD if i < passed else BAD
                sq.set_stroke(color).set_fill(color, opacity=0.2)
            rows.add(VGroup(txt(suite, 24), squares, code(f"{passed}/7", 24)))
        rows.arrange(DOWN, buff=0.35)
        for row in rows:
            row[0].move_to([-4.6, row.get_y(), 0], aligned_edge=LEFT)
            row[1].move_to([0.6, row.get_y(), 0])
            row[2].next_to(row[1], RIGHT, buff=0.4)
        rows.move_to([0, -0.4, 0])
        why = code("fails: 2 action locators + 2 template mismatches", 16, BAD).next_to(rows[3][1], DOWN, buff=0.18).align_to(rows[3][1], LEFT)
        self.at("after a redesign")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.15), run_time=1.0)
        self.at("the snapshot suite passed")
        self.play(rows[0].animate.set_opacity(0.3), rows[2].animate.set_opacity(0.3), Indicate(rows[3][2], color=PRIMARY), FadeIn(why, shift=UP * 0.1), run_time=0.9)
        self.at("test id passed six")
        self.play(Indicate(rows[1][2], color=PRIMARY), run_time=0.6)

        tree = [
            "- list:",
            "  - listitem:",
            "    - text: Write report",
            '    - button "Done"',
            "  - listitem:",
            "    - text: Ship release",
        ]
        block = terminal([indented(tree)], width=6.4).move_to([-2.4, -0.2, 0])
        done = block[1][0][3]
        scope = code("one assertion covers this subtree", 20, DIM).next_to(block, UP, buff=0.25).align_to(block, LEFT)
        changed = code("any change in here", 20, ACCENT).move_to([2.6, done.get_y(), 0], aligned_edge=LEFT)
        fails = txt("test fails", 26, BAD).next_to(block, RIGHT, buff=0.6).align_to(block, DOWN)
        self.at("a snapshot asserts")
        self.play(FadeOut(VGroup(rows, why, title), shift=UP * 0.4), FadeIn(block, shift=UP * 0.2), FadeIn(scope), run_time=0.9, rate_func=smooth)
        self.at("any change inside")
        self.play(done.animate.set_color(ACCENT), FadeIn(changed, shift=LEFT * 0.2), run_time=0.6)
        self.at("fails the test")
        self.play(block[0].animate.set_stroke(BAD), FadeIn(fails), run_time=0.6)

        term = terminal([
            prompt("npx playwright test --update-snapshots"),
            code("→ test-results/rebaselines.patch", 22, PRIMARY),
        ]).move_to([0, 1.2, 0])
        untouched = code("tests/aria-snapshots.spec.ts   not edited", 22, DIM).next_to(term, DOWN, buff=0.5)
        self.at("the update is one command")
        self.play(FadeOut(VGroup(block, scope, changed, fails), shift=UP * 0.4), FadeIn(term[0]), FadeIn(term[1][0]), run_time=0.8, rate_func=smooth)
        self.at("writes a patch file")
        self.play(FadeIn(term[1][1], shift=RIGHT * 0.15), run_time=0.6)
        self.at("does not edit")
        self.play(FadeIn(untouched), run_time=0.6)

        steps = flow(["apply patch", "fix 2 locators"], width=3.2, color=PRIMARY, size=24).move_to([-2.6, -1.6, 0])
        results = VGroup(
            code("v2 redesign   7/7 passed", 20, GOOD),
            code("v3 migration  7/7 passed", 20, GOOD),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        results.next_to(steps, RIGHT, buff=0.8)
        link = arrow(steps.get_right(), results.get_left(), DIM)
        self.at("apply the patch")
        self.play(FadeIn(steps[0][0], shift=UP * 0.1), run_time=0.5)
        self.at("fix two locators")
        self.play(grow_arrow(steps[1][0]), FadeIn(steps[0][1]), run_time=0.6)
        self.at("passed the redesign")
        self.play(grow_arrow(link), FadeIn(results[0], shift=LEFT * 0.2), run_time=0.7)
        self.at("a later migration")
        self.play(FadeIn(results[1], shift=LEFT * 0.2), run_time=0.6)
        self.end()


class S7Dial(Timed):
    def construct(self):
        dial = Line([-5, 0.6, 0], [5, 0.6, 0], color=DIM, stroke_width=4)
        ends = VGroup(
            Line([-5, 0.4, 0], [-5, 0.8, 0], color=DIM, stroke_width=4),
            Line([5, 0.4, 0], [5, 0.8, 0], color=DIM, stroke_width=4),
        )
        heads = VGroup(txt("survival", 30).next_to(ends[0], UP, buff=0.3), txt("vigilance", 30).next_to(ends[1], UP, buff=0.3))
        feet = VGroup(code("test IDs", 22, DIM).next_to(ends[0], DOWN, buff=0.3), code("whole-page snapshots", 22, DIM).next_to(ends[1], DOWN, buff=0.3))
        heads[0].align_to(ends[0], LEFT)
        feet[0].align_to(ends[0], LEFT)
        heads[1].align_to(ends[1], RIGHT)
        feet[1].align_to(ends[1], RIGHT)
        self.at("survival and vigilance")
        self.play(Create(dial), FadeIn(ends), FadeIn(heads), run_time=1.0)
        self.at("test ids sit")
        self.play(FadeIn(feet[0], shift=UP * 0.1), run_time=0.5)
        self.at("whole page snapshots")
        self.play(FadeIn(feet[1], shift=UP * 0.1), run_time=0.5)
        marker = Dot([1.0, 0.6, 0], radius=0.14, color=PRIMARY)
        here = code("scoped templates (this PoC)", 20).move_to([0.7, -0.7, 0], aligned_edge=LEFT)
        stem = Line(marker.get_bottom(), [1.0, -0.45, 0], color=DIM, stroke_width=2)
        push = arrow([0.7, -1.3, 0], [4.8, -1.3, 0], DIM)
        wider = code("wider: breaks more · catches more", 20, DIM).next_to(push, DOWN, buff=0.2).align_to(here, LEFT)
        self.at("scoped and partial")
        self.play(FadeIn(marker, scale=0.5), Create(stem), FadeIn(here), run_time=0.8)
        self.at("wider templates")
        self.play(grow_arrow(push), FadeIn(wider), run_time=0.8)
        self.play(marker.animate(rate_func=there_and_back).shift(RIGHT * 2.2), run_time=1.2)
        self.at("where you set that dial")
        self.play(Indicate(marker, color=ACCENT), self.camera_to(13.0, [0, 0.2, 0]), run_time=1.0)
        caveat = VGroup(
            code("small app", 22, DIM),
            code("regressions written by me", 22, DIM),
            code("re-run on your own app", 22, PRIMARY),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).to_edge(DOWN, buff=0.7).to_edge(LEFT, buff=1.2)
        for phrase, item in zip(["the app is small", "i wrote the regressions", "run the suites"], caveat):
            self.at(phrase)
            self.play(FadeIn(item, shift=UP * 0.15), run_time=0.5)
        self.end()


class S8EndCard(Timed):
    DRIFT = 0

    def construct(self):
        # Right half stays empty for YouTube's end-screen elements
        brand = VGroup(Dot(radius=0.1, color=GOOD), code("gary-parker", 24, GOOD)).arrange(RIGHT, buff=0.2)
        brand.move_to([-6.1, 3.0, 0], aligned_edge=LEFT)
        rows = VGroup()
        for key, value in [
            ("SOURCE", "github.com/qa-gary-parker/\npoc-aria-snapshot-assertions"),
            ("WRITE-UP", "garyparker.dev/blog/\naria-snapshots-assertion-layer"),
        ]:
            rows.add(VGroup(code(key, 16, DIM), code(value, 24, line_spacing=0.8)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT).next_to(brand, DOWN, buff=0.9).align_to(brand, LEFT)
        summary = code("test IDs 0/5  ·  ARIA snapshots 5/5", 20, DIM).move_to([-6.1, -3.0, 0], aligned_edge=LEFT)
        self.add(brand, rows, summary)
        self.end(minimum=10.0)
