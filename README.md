# poc-aria-snapshot-assertions

**The question:** locator debates are about which selectors *survive* change. Almost
nobody asks the opposite question — what does your suite still *see*? Playwright's
ARIA snapshots assert on the accessibility tree instead of individual elements.
What breaks, and what stops being missed?

**The answer:** under UI drift, snapshot assertions broke *more* than plain ARIA
locators (they assert more of the tree). But when the app shipped five user-facing
accessibility regressions, the snapshot suite caught **5/5** — while the test-id
suite, the one that survives refactors best, caught **0/5**. Survival and vigilance
are opposite ends of the same dial. And the update workflow is a reviewable patch,
not an agent editing your code.

> Exploratory PoC, throwaway by default. Written up in
> [ARIA snapshots: the assertion layer your locators are missing](https://garyparker.dev/blog/aria-snapshots-assertion-layer).
> Uses the same TaskBoard drift testbed as
> [poc-self-healing-selectors](https://github.com/qa-gary-parker/poc-self-healing-selectors).

## Method

The TaskBoard demo app in three drift versions (v1 → v2 redesign → v3 CSS-modules
migration), plus the three locator-strategy suites from the self-healing PoC
(CSS-legacy, ARIA-first, test-ids). New here:

1. A fourth suite, [`aria-snapshots.spec.ts`](tests/aria-snapshots.spec.ts) —
   same 7 scenarios; actions use user-facing locators, assertions are scoped
   `toMatchAriaSnapshot` templates written against v1.
2. Five app variants ([`app/r1-heading` … `app/r5-label`](app/)), each seeding one
   **user-facing accessibility regression that changes nothing visually**:
   heading demoted h2→h4, list markup flattened to divs, a button swapped for a
   clickable div, `role="alert"` removed, a label's input association broken.
3. The AI-mode snapshot ([`scripts/capture-ai-snapshot.mjs`](scripts/capture-ai-snapshot.mjs)) —
   `ariaSnapshot({ mode: "ai", boxes: true })`, the element-ref + bounding-box
   view Playwright now exposes for agents.

## Results

**1. Drift survival** (suites written once against v1):

| Suite | v2 (redesign) | v3 (CSS-modules) |
|---|---|---|
| CSS legacy | 0/7 | 0/7 |
| ARIA-first | 5/7 | 5/7 |
| test-ids | 6/7 | 6/7 |
| **ARIA snapshots** | **3/7** | **3/7** |

Snapshots came second-worst. Two failures were the same accessible-name changes
that broke the ARIA-first suite (they share action locators); two more were
template mismatches — a snapshot asserts the whole subtree, so any drift inside
it fails the test. Assertion breadth has a drift cost.

**2. Update cost.** One command — `npx playwright test --update-snapshots` (31s
here) — regenerated every stale template. Crucially, Playwright **does not edit
your test file**: it writes `test-results/rebaselines.patch` for human review.
Apply the patch, fix the two action locators (one line each, the same repairs the
ARIA-first suite needed), and the suite passed v2 **and** v3 with no further
changes. Compare the self-healing PoC: the healer edits code directly and the
CSS suite needed a full re-heal every release (4m36s + 3m23s).

One catch worth knowing: the rebaselined templates are *full-tree*, not the
minimal partials I wrote — the tooling trades your curated assertion for maximum
density, the same assert-everything instinct the
[test-agents experiment](https://garyparker.dev/blog/hands-on-with-playwright-test-agents)
found in the generator. Trim after applying.

**3. Regression detection — the result that matters.** Five variants, each with
one seeded user-facing accessibility break, all visually identical:

| Regression | CSS legacy | test-ids | ARIA-first | ARIA snapshots |
|---|---|---|---|---|
| Heading demoted h2 → h4 | miss | miss | miss | **caught** |
| List markup → divs | caught | miss | caught | caught |
| Button → clickable div | miss | miss | caught | caught |
| `role="alert"` removed | miss | miss | caught | caught |
| Label association broken | miss | miss | caught | caught |
| **Total** | 1/5 | **0/5** | 4/5 | **5/5** |

The test-id suite ran **7/7 green through all five regressions combined**
(`app/v1-regressed`). It survives refactors precisely because it looks at a
private contract instead of what users experience — maximum stability, maximum
blindness. Only snapshots caught the heading demotion: `getByRole("heading",
{ name: "My Tasks" })` happily matches an h4, but the template pins `[level=2]`.

**4. The agent angle.** `ariaSnapshot({ mode: "ai", boxes: true })` returns the
tree with element refs and viewport coordinates:

```yaml
- textbox "New task" [ref=e6] [box=400,168,153,21]
- button "Add" [ref=e7] [box=557,165,52,27]
- list [ref=e12] [box=400,229,480,96]:
  - listitem [ref=e13] [box=440,229,440,33]:
    - generic [ref=e14]: Write report
    - button "Done" [ref=e15] [box=832,235,48,21]
```

This is the page representation MCP-driven agents act on — roles and names for
semantics, refs for interaction, boxes for layout. If your app is illegible in
this format, it's illegible to agents *and* to assistive tech. Same dial again.

## Caveats

- Small app, authored drift and authored regressions — realistic patterns, but
  synthetic and chosen to differentiate the strategies.
- Snapshot templates here are scoped and partial; whole-page snapshots would
  fail more under drift and catch more regressions. Where you set that dial is
  the actual engineering decision.

## Reproduce

```bash
npm ci && npx playwright install chromium
APP_VERSION=v1 npx playwright test                          # 28/28 pass
APP_VERSION=v2 npx playwright test aria-snapshots           # drift: 4 fail
APP_VERSION=v2 npx playwright test aria-snapshots --update-snapshots  # writes rebaselines.patch
APP_VERSION=r1-heading npx playwright test                  # only snapshots catch it
APP_VERSION=v1-regressed npx playwright test test-ids       # 7/7 green through 5 a11y breaks
SUITE_DIR=tests-updated APP_VERSION=v3 npx playwright test  # updated suite vs later drift
node scripts/capture-ai-snapshot.mjs                        # AI-mode snapshot with boxes
```

MIT. Public demo app written for this experiment — no real product code.
