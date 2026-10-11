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
