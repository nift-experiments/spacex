# HANDOVER.md
v0.0.8

This is a living handover for working effectively in a Nift project.

Canonical version:

https://nift.dev/HANDOVER.md

Check the version at the top of this file against the canonical copy when the
project is old, unfamiliar, or behaving differently from the current Nift
documentation.

To replace this file with the latest canonical version:

```sh
curl -fsSL https://nift.dev/HANDOVER.md -o HANDOVER.md
```

If this project has project-specific additions, preserve or reapply them when
updating the canonical handover.

This project uses Nift as part of its website build process.

Nift is the project's build-time templating and dependency layer. It does not determine what the website is about or what other technologies the project should use.

Keep the existing project architecture and use the project's normal HTML, CSS, JavaScript, frameworks, backend, and other tooling where appropriate.

Do not introduce Nift-specific machinery where ordinary web tooling is the clearer solution.

## Start here

Before making substantial changes:

1. Inspect `.nift/config.json` and `.nift/tracked.json`.
2. Inspect the existing `content/`, `templates/`, and output structure.
3. Read this project's `README.md` and other project-specific documentation.
4. Run:

```sh
nift status
```

During normal development, build frequently:

```sh
nift build
```

Use this throughout a task, not only at the end. Rebuild after meaningful
changes so Nift can surface template, path, dependency, configuration, and
tracking errors while the cause is still obvious.

In particular, run `nift build` immediately after editing
`.nift/config.json` or `.nift/tracked.json`.

Use:

```sh
nift status
```

when you want to inspect what Nift considers stale and why.

Successful `nift build` output may include indented `↳ ...` lines explaining
why a page was considered stale and rebuilt, such as a missing generated output
or a changed dependency. These are rebuild reasons, not errors. Actual build
failures are reported as errors and cause the build to fail.

Do not delete or recreate `.nift/`.

## Nift's core template model

Most Nift websites need very little Nift-specific syntax.

The three primitives you will use most often are:

```text
@content
@input(...)
@path(...)
```

`@content` inserts the tracked page's content into its template.

```html
<main>
    @content
</main>
```

`@content` should execute exactly once across the rendered template/input graph
for a tracked page. It is normally placed in the page's template; the tracked
content file supplies the content inserted there.

Content files may still use other Nift syntax when needed. If page text needs
to display Nift syntax literally, prefix the active sigil with `\` rather than
leaving it as template syntax:

```html
<code>\@content</code>
<code>\@path('about')</code>
<code>\$[title]</code>
```

This applies whenever `@...`, `$[...]`, or other Nift syntax is intended as
literal output rather than something Nift should execute or resolve.

`@input(...)` inserts a reusable file and automatically makes it a dependency of the output using it.

```html
@input('templates/header.html')

<main>
    @content
</main>

@input('templates/footer.html')
```

### Structured JSON and markup sources

Use name-first `@json` when a template needs immutable structured data:

```text
@json(name, path)
@json(name, schema-path, path)
@json(name, schema-name, path)
@json(name){...}
@json(name, schema-path){...}
@json(name, schema-name){...}
```

Inline bodies are evaluated as Nift templates before JSON parsing. A schema
name refers to an earlier JSON binding. Data and schema files are automatic
dependencies and paths must stay inside the project.

Use `@markup(format){...}` or `@markup(format, path)` for Markdown (`md`),
AsciiDoc (`adoc`) or reStructuredText (`rst`). Nift evaluates template syntax in
the source first, Markup++ converts it once, and the resulting HTML is appended
without being parsed as Nift syntax again. File sources and host-resolved
AsciiDoc/RST includes are automatic dependencies.

`@path(...)` creates project-aware links to tracked pages and local assets.

Nift has additional features including metadata, JSON data, loops, conditionals, pagination, contracts, and explicit dependencies. Use them when the project actually needs them; do not use advanced features merely because they exist.

When writing expressions inside constructs such as `@if(...)`, refer to values directly rather than wrapping them in `$[...]`. For example:

```html
@if(name == 'about'){...}
```

Use `$[...]` when resolving or rendering a value into output, for example `$[title]`. Consult the expressions and control-flow documentation when using more advanced expression syntax.

## Internal links: use `@path`

Use `@path(...)` for internal links.

This applies to:

- links between pages;
- stylesheets;
- JavaScript;
- images and other local assets where Nift should know the relationship.

For pages, link to the **tracked page name**, not its generated file.

```html
<nav>
    <a href="@path('/')">Home</a>
    <a href="@path('about')">About</a>
    <a href="@path('docs')">Docs</a>
    <a href="@path('contact')">Contact</a>
</nav>
```

Do this:

```html
<a href="@path('about')">About</a>
```

Do not do this:

```html
<a href="@path('about.html')">About</a>
```

and do not hard-code the generated output path:

```html
<a href="about.html">About</a>
```

The tracked page name is the stable project identity. Its output filename or location may change independently.

CSS and JavaScript includes should also use `@path(...)`:

```html
<link rel="stylesheet" href="@path('public/assets/style.css')">
<script src="@path('public/assets/app.js')"></script>
```

Do not calculate relative paths such as:

```html
<link rel="stylesheet" href="../../assets/style.css">
```

Using `@path` lets Nift resolve the correct output-relative path and check the project relationship during the build.

## Project configuration

`.nift/config.json` contains project-level Nift configuration.

`.nift/tracked.json` describes tracked pages and their metadata, including things such as their content, template, and output relationships.

By default, ordinary CSS, JavaScript, images, fonts and other static assets live
directly in the configured output tree (normally `public/`) and do not have
entries in `.nift/tracked.json`. Edit those files in place. This keeps Nift's
tracked graph focused on content that Nift actually renders and avoids duplicate
source/output copies for files that need no build-time transformation.

Track an asset only when Nift genuinely needs to generate it from content,
templates or build-time data. Template-less tracked entries remain available for
that advanced case; they are not the default asset workflow.

These files are part of the project and should evolve with its structure.

If you add, remove, or reorganise pages, templates, outputs, deployment settings, or other Nift-managed structure, inspect the relevant `.nift` configuration and update it where necessary.

Do not treat `.nift/` as disposable generated state.

Do not invent `.nift/tracked.json` fields or assume arbitrary fields become
`$[...]` metadata. When you need tracking behaviour or metadata that is not
already demonstrated by the project, consult the tracked-files and metadata
documentation rather than guessing.

## Output directory

Do not assume the generated website always lives in `public/`.

A normal Nift project may use `public/`, but deployment targets can use a different output structure appropriate to the platform.

Inspect `.nift/config.json` before making assumptions about output paths.

Edit Nift-managed page sources rather than their generated output. Edit untracked
static assets directly in the configured output tree, unless the project
documents another tool or source directory as their owner.

## Pagination

Pagination has several related pieces across `.nift/tracked.json`, page
content, pagination templates, and generated page links. Do not infer its full
behaviour from this handover.

If working with pagination, read the dedicated documentation first:

https://nift.dev/docs/pagination.html

Preserve the project's existing pagination structure unless the task actually
requires changing it, and run `nift build` frequently while doing so.

## Other stacks and tools

Nift does not need to own the whole application.

A project may use Nift alongside tools such as Vite, React, Vue, Svelte, TypeScript, Go, Node, Python, PHP, serverless functions, or other systems.

Keep responsibilities separated:

- use Nift for build-time composition, tracked relationships, and dependencies;
- use the neighbouring tool for the job it is designed to do.

Do not replace an existing stack with Nift-specific code simply to make more of the project use Nift.

## Before finishing

Run:

```sh
nift build
nift status
```

The build should succeed and `nift status` should report the project up to date.
Spot-check generated output when changes affect paths, templates, tracked
relationships, or deployment structure.

## Documentation

Nift documentation:

https://nift.dev/docs.html

When unfamiliar with the project, prioritise:

1. Getting started — https://nift.dev/docs/getting-started.html
2. the three-primitives/template-language material;
3. paths and tracked files, especially `@path`;
4. project structure;
5. `.nift/config.json` and `.nift/tracked.json`;
6. incremental builds and CLI commands.

Then read feature documentation only when the task requires it, for example:

- JSON and control flow;
- pagination;
- contracts;
- minification;
- deployment targets;
- integration with other application stacks.

Prefer documented Nift behaviour and the existing project structure over guessing based on another website generator or framework.

## SpaceX campaign S0

Initialized authored reconstruction from observable production. See investigation/STATUS.md. Baseline capture is in sibling spacex-baseline; scaffold is placeholder. Exact next action: reconcile lazy routes, public CMS inputs and required media before translating content. No private source/build benchmark is available.

### Runtime-media scope decision

The user authorized remote-reference preservation for large downloadable catalogue media; playback-critical assets remain frozen locally. The storage pause is resolved. Continue S1 acquisition and interaction reconciliation, then homepage-first native implementation. Heavy reference remains in ../spacex-baseline. No completed S1/S3 claim.

Current implementation: homepage plus 710 mission pages built in both source models. Marketing-family recovery is in progress from public DOM captures, with semantic scoped CSS and native @path references. Do not count empty publication directories as pages. Do not accept partial asset transfers, zero animation-state statistics, or inert media controls as parity. Heavy reference remains outside both maintained projects; Git asset packaging is unresolved and large files must not be added blindly.

### Current route and media checkpoint

Both registries contain 806 page/redirect outputs and 89 HLS outputs. Native forms use declarative shadow DOM recovered from the public open shadow roots; private submissions remain outside the reproduction contract. Browser parity is still open. Media playback/quality/download controls are implemented; playlists preserve the authored JSON versus maintained HTML distinction. See STATUS.md for the remaining closure work.

### Legacy-route and navigation checkpoint

Both projects now build 828 page/redirect outputs plus 89 HLS manifests (917 tracked outputs). This includes 711 real missions, the new Starship SN6 source, and 21 legacy destinations reconciled against public behavior. All 805 initial unique route paths have maintained outputs. The 34,500-reference audit leaves two inherited public-source defects, documented in investigation/evidence/inherited-source-defects.json; these are not claims of complete browser parity.

Upcoming-launch cards now use the frozen future-mission ordering and pad images. Desktop heading/header geometry matches the captured reference; representative native keyboard dropdown open/Escape behavior passes. Responsive testing remains open because the browser viewport override did not change the actual viewport. Shared asset release upload is being retried serially after GitHub timed out; do not claim clean-network asset setup until all 13 parts are verified remotely.

### Complete launch-table and webcast controller checkpoint

There are now 829 page/redirect outputs and 89 HLS manifests (918 tracked outputs), including 712 real mission pages. EchoStar 105 / SES-11 requires its original trailing-space ID: exact API ID returns 200, trimmed ID returns 404. All 729 completed launch records are represented, with local search/filter/pagination and native route paths. Representative authored next-page, page-size, text search and category filtering pass; Starship search matches the frozen reference (20 results). Rendered launch-table checks are still being completed.

Webcast controllers cover maintained metadata for 661 mission pages; representative authored/rendered Flight 14 opening, canonical external embed URL and dismissal/focus checks pass in explicit offline-service previews. No external service success is fabricated. Mobile header checks now run in the selected 390×844 tab. The mobile homepage alignment and missing upcoming block are corrected; final viewport/pixel parity remains open.

Asset transport is now 50 parts of at most 64 MiB, with unchanged content identity and publication bytes. The smaller-part upload is in progress; clean-network setup is not yet accepted.

### Bounded vehicle-state and mobile-media checkpoint

Seventeen captured variants cover seven Falcon 9/Falcon Heavy/Dragon tab groups (22 template instances including the Dragon alias). Authored variants are maintained partials; rendered variants are inline maintained HTML. The native controller replaces only the affected component and preserves tab focus. Thirty-four normalized content comparisons against the public captures pass; representative Falcon 9 and rendered Dragon switching checks pass. This does not close final visual parity.

Captured runtime properties restore 424 muted assignments across both projects while preserving the three unmuted public capture exceptions. The native flight-video overlay opens the original embed URL and closes with Escape/focus return in the offline-service preview. Sixty-two maintained slide caption assignments now update the gallery caption on navigation.

The literal mobile-media inventory yields 345 @path bindings across both projects. A separate shared supplement contains 108 frozen mobile assets (329,265,903 bytes), including two newly verified Dragon gallery images. The original base identity remains unchanged. Both release transport and clean-network acquisition remain open; routine Nift builds never run asset acquisition or migration recipes. Remaining component families, complete form conditions, mission galleries/tracker/crew and final parity/lifecycle/benchmarks remain open.

### Supplier conditional-editing checkpoint

Native NAICS and CSI repeat fields now use observed public field structures. The authored project composes two maintained row partials; the rendered project maintains their HTML inline. Public source and browser state establish the one-row NAICS deletion floor, conditional industry-specialization requirement, construction options and complete CSI select list. Representative desktop authored and mobile rendered add/condition checks pass. Hidden controls are disabled for native validity checks; acknowledgement boxes remain untouched and no submission is performed. Complete validation/pixel parity remains open.

### Starship native selection checkpoint

Two additional Raptor variants bring the maintained tab inventory to 19 captured states. Four Starship pagination groups are recovered from public open shadow DOM as native controls, with only their presentation CSS retained. Representative authored direct selection of slide 4 and RVac content (275 tf / 606 klbf) passes. Final responsive/pixel parity remains open.

### Clean-checkout portability correction

A fresh GitHub clone exposed internal @path arguments using `public/<route>/`, which had depended on pre-existing output directories. Maintained internal route references now use tracked names. Captured srcset references to the local reference server are converted to native @path asset references; the publication audit now checks srcset and rejects local reference-server dependencies. One 3,748,368-byte responsive image is transported separately, and small responsive images are maintained Git assets. The two documented inherited source defects remain visible. This is a migration-source correction; no Nift core changes were made. Clean-checkout completion is still being verified, and final parity/benchmark acceptance remains open.

### Mission states, newsletter UI, and clean-checkout paths

Mission Droneship/Landing Zone states are maintained through the existing native tab controller; 42 real-capture text/value comparisons pass across both projects. The observed newsletter form is recovered at 35 hosts, with native email validation and an explicit unavailable-service response. It never sends subscription requests. Authored prose route bindings now use tracked names in `@path`, including the legacy rideshare index suffix. A clean checkout exposed 97 such prose bindings previously masked by existing output directories. Both clean-checkout builds/audits pass after correction; final browser parity remains open.

All base (51), mobile (6), and responsive (2) release assets pass remote size/SHA256 verification. Empty-cache network acquisition is being checked separately; hash verification alone is not claimed as that proof.

### Human Spaceflight and Starmind captured tab families

Four Human Spaceflight mission states and three Starmind AI1 states now use maintained HTML variants through the existing native controller. Starmind uses an explicit `.sticky-viewport` section selector rather than a framework interpreter. Its thermal and solar images were frozen with successful HTTP 200 receipts and SHA256 identities, and are small maintained Git assets. Fifty-six capture-derived text/value comparisons pass across both projects. Authored Space Station and Starmind Thermal states and rendered mobile Mars were exercised in the browser; comprehensive parity remains open.

### Bounded marketing states, public dialogs, and runtime asset closure

Thirty-six captured maintained tab variants now cover vehicle components, Mission landing, Human Spaceflight missions, Starmind, Mid-South campus/environment, and Florida pads. Seventy-two real-capture text/value comparisons pass across both projects. Shared unscoped public CSS was omitted by the initial scoped-style recipe; the exact two blocks are now maintained once and included at the three affected page families (Mid-South, Sites, Starbase). Browser checks confirmed desktop Mid-South campus/environment changes and the Florida SLC-37 image/Coming Soon state.

Mid-South partner and feedback dialogs preserve 30 captured choices, the Other-organization required field, public validation messages/rules, and phone/ZIP formatting. Authored browser checks cover opening, selection, Escape/focus restoration, the six-error invalid Other state, and an explicit unavailable response for valid synthetic feedback; rendered mobile opening and organization choices were checked. No real submissions, CAPTCHA completion, telemetry, or fake success occurred. Complete visual/keyboard/validation matrices remain open.

Forty remaining runtime image/audio/video URLs were frozen with completed HTTP 200 receipts (61,542,940 bytes) and 44 source bindings converted to `@path`. This includes the 24,197,832-byte Mid-South background WebM. Zero raw remote runtime `src` bindings remain in content/prose/templates. Download-only MP4 links and deliberately remote HLS tails remain as disclosed. Additional launch-tab and runtime bundles have published, hash-verified releases; routine builds never acquire them.

A clean network asset-acquisition attempt failed for temporary disk exhaustion during extraction. The failed log is retained externally. Only unchanged ignored asset copies in a temporary authored verification checkout were removed (3,684,197,090 bytes); the retry verified base/mobile/responsive release acquisition successfully. Downloaded base transport parts were independently object-verified and then removed; setup now discards network transport copies after extraction by default without touching canonical bundles. Working repositories, frozen bytes, and canonical evidence were retained. Final clean-checkout parity, animation closure, lifecycle tests, and benchmark campaign remain outstanding.

### Public Sites reveal and asset transport verification

The two public Sites reveal observers now retain their captured thresholds, root margins, one-shot classes, and reduced-motion branch. Authored Sites browser observation confirms initially hidden feature content reveals after scrolling into the viewport. Mid-South environment scroll transitions and the complete responsive parity matrix remain open. All five maintained asset bundles have now passed network acquisition and hash verification, including the launch-tab and runtime supplements. The earlier disk-exhaustion attempt remains recorded; this does not imply final browser parity acceptance.

### Mid-South environment scroll controller

The public 5789 bundle supplies the exact chapter hysteresis, 340 ms departure transition, reduced-motion branch, mobile cutoff, and wheel/touch click-lock release. These are maintained in a bounded native controller. Authored browser checks verify manual Power selection/focus and automatic Air selection without focus transfer; programmatic scrolling correctly retains the manual click lock. Complete touch/viewport transition parity remains open.

### Carousel controls, active launch navigation, and checkout verification

Human Spaceflight has recovered 4-slide and 12-slide pagination groups; Mission has its captured 9-slide group. Authored browser direct selection of timeline slide 12 displays the 2023 Starship test and disables Next. Four ongoing/upcoming rows now resolve their frozen CMS destinations using @path; Crew-13 navigation is confirmed in the reference by click and in authored output by Enter (the public row did not navigate on Enter). Dynamic countdowns remain open.

Fresh verification checkouts at authored aa9c5b9 and rendered 2e4e439 acquire all five pinned bundles, build all 918 outputs, and pass publication audits. Their only generated audit-file changes were preserved outside the checkout then restored, leaving both verification trees clean. Raw logs and acquisition data remain under spacex-baseline/verification. This verifies that checkpoint, not final parity acceptance.

### Corpus-wide mission crew recovery

Twenty-one missions now preserve their 80 public crew portraits and cards. Authored records retain maintained structured portrait paths and shared Nift composition; rendered-source cards remain maintained HTML. The 50,236,841-byte portrait supplement is shared release transport, independently size/digest verified, and excluded from Git payloads. All four authored Crew-13 portraits load at captured width 4000. One complete resumed portrait has a 206 receipt; full byte length/hash verification is retained. Whitespace-prefixed bio links preserve the observed public sanitizer defect. Nullable timeline disclaimers no longer render the generated text "null"; source Crew-13 confirms absence. Mission galleries, tracker, countdowns, final responsive states, lifecycle and benchmarks remain open.

### Corpus-wide native mission galleries

All 143 mission galleries now use native carousels with 411 maintained slides and direct-selection bullets. Four empty CMS media entries remain blank slides. Shared public gallery styles preserve launch-tile geometry; shared native carousel CSS is explicitly included. Authored sources keep structured gallery records and a shared Nift partial, while rendered sources keep complete gallery HTML. Output slide/bullet/image counts match maintained records in both projects. Authored Crew-13 final-slide selection disables Next, loads the 2600-pixel captured image in the viewport, and has the same 941-pixel gallery height as the observed reference viewport. Complete responsive/interaction parity remains open.

### Multi-webcast public lists

The pinned launch-detail component displays webcast rows only when there is more than one stream. All 22 affected missions now retain 81 rows, exact public thumbnails/mobile variants, optional dates, and supported stream controls. Authored composition uses native loop.length rather than a duplicated visibility flag; agent rows remain maintained HTML. Authored Crew-13 Docking opens the same canonical embed URL as the reference, closes with Escape, removes the iframe, and restores focus. Offline CSP blocks external playback in both tests, so playback itself is not claimed. The 124 additional webcast assets total 56,181,535 bytes; their shared release has remote digest and network acquisition verification. Complete tracker/diagram/countdown and responsive parity remains open.

### Native public tracker runtime checkpoint

Vehicle Tracker and Follow Dragon now retain the delivered public Three/WebGL renderer with scoped native roots. The invalid captured nested body was replaced with a div; 17 texture references resolve to 11 small maintained assets through @path. Three exact public telemetry responses are maintained as explicit offline snapshots. Production keeps the original public GET endpoints; offline preview injects a frozen-service marker without changing published HTML. Normal builds neither fetch telemetry nor recover runtime assets. Authored projects compose shared tracker partials; rendered projects maintain their HTML, including all four enabled mission embeds. Browser checks confirm real canvases and exact frozen telemetry for both standalone families and rendered Crew-13. This is representative runtime evidence, not final responsive or interaction parity. The strengthened whole-HTML audit also found and corrected a leftover reference-origin Starmind URL attribute. Mission diagrams, countdowns, full parity, lifecycle, and final benchmarks remain open.

### Space Station diagram desktop recovery checkpoint

The frozen public launch-detail component uses toTheIssEnabled on 26 missions. All 26 now contain the captured shared six-step flight diagram and seven native @path images. Desktop Crew-13 verifies all images loaded, six descriptions matching the reference, and native keyboard highlight/dim behavior. Authored JSON explicitly records the diagram visibility flag; agent pages maintain complete rendered markup. Public source ignores returnFromIssEnabled and toTheIssTense, and the pinned corpus has no nonempty mission.media entries; no speculative implementation was added for those fields. The responsive mobile diagram controls remain OPEN. The browser viewport capability returned without changing innerWidth (1280), so no new mobile parity claim is made. Next: recover the delivered mobile diagram branch, verify actual viewport dimensions before responsive claims, then continue countdown/form/lifecycle closure. Final parity and benchmarks remain open.

### Homepage scroll/header and footer defect correction

User reported the missing scroll hide behavior and broken footer. The delivered public header onScroll hides on downward scrolling at or above 50px, reveals upward/below 50px, and retains visibility while mobile navigation is expanded. Both native controllers now preserve that rule and the public header-hide class. Footer markup now matches the reference's separate social control, navigation row, and copyright block; the public social SVG and target semantics are retained. Native footer containment preserves margins as the original flex shell does. Desktop authored downward opacity reaches 0; upward reveal matches reference. Rendered mobile at actual 390x844 hides downward/reveals upward. Footer height matches reference at desktop 72px and mobile 132px. No core changes. A mobile Crew-13 capture was subsequently obtained through the tab with the actual 390x844 viewport; desktop tab overrides did not resize that tab. Next diagram source: launches-crew13.390x844.44b2c0fdb858.json.

### Mobile Space Station diagram closure

All 26 applicable missions now retain both delivered diagram branches: desktop node highlighting and the six-step mobile controls. The observed mobile markup is pinned to launches-crew13.390x844.44b2c0fdb858.json. Native @path binds the initial SVG and the exact 165,763-byte captured nosecone JPEG, selected after step three. At actual 390x844, the reference and rendered migration match step four and its image change; rendered step six disables Next, and authored step two matches the reference text. Shared button styling retains the observed 50px height. Complete responsive visual/interaction parity remains open; no claim is based on a requested viewport without verifying innerWidth. Normal builds use maintained sources directly. Next: dynamic mission/launch countdown behavior, outstanding form/viewport checks, then lifecycle and final performance work.

### Public launch clock and date/window behavior

The initialized source reveals two real rolling countdowns on the launch page, previously empty in migrated markup. Both projects now retain the public per-digit 13px rolling geometry and clock calculation, timezone/DST conversion, overrides, paused T-zero handling, date/window labels, and final/ongoing selection. A compact maintained schedule contains 732 pinned tile records. Authored structured mission/upcoming records bind their keys; rendered pages maintain their bindings and HTML. Offline preview consumes frozen inputs and advances the local clock. Production preserves the canonical timing GET and captured adaptive polling intervals; normal builds never acquire timing metadata. Desktop authored digits match the reference within one second across sequential reads; rendered mobile at actual 390x844 initializes both T-minus and T-plus clocks. Pinned real-record tests cover windows, dates, daylight/standard offsets, and clock sign. Comprehensive timing/visual parity and lifecycle remain open.

Mobile launch-table window labels match the source date-only branch; homepage cards retain full windows. The archived Demo-2 date range matches (May 30, 2020 - August 2, 2020).

### Public careers corpus and filter recovery

The public lazy careers module uses job_metadata_new.json and job_posts_new.json, which the initial response inventory missed. Both 200 responses now have canonical capture receipts outside the projects; the 874,048-byte postings response supplies 3,059 records in 57 discipline groups (3,058 unique job IDs; the public duplicate is preserved). This explicitly extends the reference inputs; the initially empty board was not accepted parity. Authored sources maintain structured job records and Nift loops; rendered sources maintain complete job HTML. Original external application links remain intact without exercising applications. Internal navigation and maintained metadata use @path. Normal builds perform no acquisition or migration conversion.

All published titles, locations, disciplines, program memberships and application URLs match the captured record multiset. Desktop authored Raptor returns 78 jobs; Raptor plus Starship returns 76 with exact reference title/URL order. Rendered mobile at actual 390x844 returns 76, clears to all 3,059, and Apply closes the panel. Authored homepage program/keyword search reaches the expected filtered board. Keyboard actions pass; mobile coordinate-click automation did not activate off-screen footer controls, so no touch-action claim is inferred. Full visual/filter/viewport parity and lifecycle remain open.
