# Design notes

How the desktop app and the generated notice are put together, so a change lands in the
same shape as what is already there. The rules here are enforced where they can be: the
axe check in `electron/e2e/a11y.e2e.mjs` measures contrast in the running app, in both
themes, on every CI run.

## Tokens

Colours, radii and spacing are named in `frontend/src/index.css` and nowhere else.
Components use the names, never a palette value:

```jsx
<p className="text-fg-muted">   // yes
<p className="text-zinc-400">   // no
```

Each token carries its light and its dark value in a single `light-dark()` pair, so the
two cannot drift apart:

```css
--onot-fg-muted: light-dark(#52525b, #a1a1aa);
```

`color-scheme` is the switch that chooses between them. It is left open on `:root`, which
makes the app follow the operating system with no JavaScript and no chance of a wrong
first paint; an explicit choice writes `data-theme="light"` or `"dark"`, which pins it.
Because the same property drives the native controls, checkboxes and scrollbars follow the
app rather than the OS. There is deliberately no `dark:` variant in the codebase, and no
`darkMode` setting in the Tailwind config: a variant would only see part of this picture.

| Token | Use |
|--|--|
| `surface` | the page |
| `surface-raised` | cards and anything sitting on the page |
| `surface-sunken` | hover fills, chips |
| `fg` | body text |
| `fg-muted` | labels, hints, secondary text |
| `border` | dividers and decorative edges |
| `border-strong` | control edges, which must clear 3:1 on their own |
| `brand` / `on-brand` | the primary button fill and its text |
| `brand-hover` | that button's hover fill |
| `accent` | links, and the focus ring |
| `danger-fg` / `danger-bg` / `danger-border` | the error banner |
| `warning-fg` | warnings |
| `success-fg` | confirmations |

Radii come in two steps, `rounded-control` for buttons and inputs and `rounded-card` for
cards. Spacing uses `2`, `3`, `4` and `6`. Type uses `text-xs` for secondary labels,
`text-sm` for body and controls, `text-base` for card titles and `text-2xl` for the page
title.

## Colour and contrast

Every text token clears 4.5:1 against the surface it is used on, and every control edge
clears 3:1, in both themes. Two things are easy to miss when picking a value:

- Hover states count. `brand-hover` in dark started as indigo-500 and measured 4.46:1
  against white text, which the axe run caught and a palette review had not.
- A control mid-transition reports a blended colour. That is a measurement artefact, not
  a design fault, which is why the audit waits for controls to settle rather than
  loosening the threshold.

The brand colour is the indigo of the logo, `#4f46e5`. The app, the logo and the links in
a generated notice all use it, and `notice.css` names its colours as variables for the
same reason the app does.

## Wording

Format names are spelled the way a reader spells them: HTML, Text, Markdown, PDF, never
the API's `html` or `pdf`. Buttons name what they do to something ("Save notice",
"Preview"), and the primary button is the thing the user came for, not a step on the way.
Every string lives in `frontend/src/lib/i18n.ts`; the notice's own strings live separately
in `src/onot/rendering/i18n/en.yaml`, because one is the app and the other is the
document.

The project is English-only and CI enforces it (`scripts/check_no_hangul.py`). Prefer a
plain hyphen to an em dash: terminals and PDF fonts handle it more predictably.

## The generated notice

`notice.css` is the whole theme. It is inlined into the HTML output, so a saved notice is
one self-contained file.

Its `@media print` block is the single source of the paged rules, because both routes to a
PDF read it: WeasyPrint on the CLI, and Chromium's `printToPDF` in the desktop app.
`pdf.css` adds only what is specific to WeasyPrint's paged media, the `@page` box and its
numbered footer, and the desktop side passes matching margins and a footer template to
`printToPDF`. When you change page geometry, change both or they drift.

Two traps in this file have already been paid for:

- Do not apply `page-break-inside: avoid` to a licence block. A full licence text runs past
  a page, so the rule pushes each one to a fresh page and leaves the previous one half
  empty.
- The stylesheet is passed through the template with `| safe`. Autoescaping it turned every
  quoted font name into `&#34;`, and because `<style>` is a raw-text element the entity is
  never decoded, so the whole `font-family` declaration was invalid and notices rendered in
  the default serif. Nothing else in the template may skip escaping.
- An `@page` margin box does not inherit from `body`, which is why the font stack is a
  variable that `pdf.css` reads rather than a value written once on `body`.

## The preview

The preview frame shows the same document the user is about to save, so the notice's own
links have to work inside it. Four things have to hold at once, and each of them once did
not:

- The frame loads a **blob URL**, not `srcdoc`. An `about:srcdoc` document takes its base
  URL from the parent, so a link to `#licenses` resolved against the app's URL and
  navigated the frame to the app, leaving the preview blank.
- The CSP allows `blob:` in `frame-src`.
- The sandbox grants `allow-same-origin`. A fully opaque origin refuses the document's own
  anchor links, which leaves the contents list looking fine and doing nothing. It must
  never also grant `allow-scripts`: that pairing lets a frame lift its own sandbox. With
  scripts withheld nothing in the notice executes, which is the actual protection.
- `will-navigate` in the main process lets a subframe move within a `blob:` URL.

`electron/e2e/preview-navigation.e2e.mjs` asserts the outcome rather than any one of these,
because a regression in any of them looks identical from the user's side.

## Checks

- `bash scripts/gate.sh` runs the lot.
- `electron/e2e/a11y.e2e.mjs` audits the running window with axe in both themes, checks
  that the drop zone shows a focus indicator under keyboard navigation, and checks that
  `prefers-reduced-motion` collapses the transitions.
- The jsdom unit tests disable axe's `color-contrast` rule on purpose: jsdom has no
  rendered colours, so the rule is silently skipped rather than checked. That coverage is
  the E2E's job.
