# BASELINE.md

The frozen upstream reference. Complete this before migrating content.

## Upstream reference

- Upstream repository:
- Upstream commit SHA:
- Upstream source directory:
- Production build command:
- Toolchain / runtime versions:
- Tool/binary hashes (where relevant):

## Source model

Choose exactly one and describe it:

- [ ] authored (human + agent; Markdown/MDX/frontmatter preserved)
- [ ] rendered (agent-primary; rendered HTML/CSS/JS + explicit metadata/nav)
- [ ] hybrid (describe):

Publication/behaviour parity does not require different source models to
preserve identical source semantics.

## Complete production pipeline

A successful build is not necessarily the complete publication. List every
production step in order (build, search/index generation, post-processing,
API/reference generation, downloads/exports, asset processing, deployment
transforms, registry-generated data, client-island/bundle preparation, multi-stage re-builds):

1.

## Frozen reference output

REFERENCE OUTPUT (immutable, upstream):
    <absolute path>
MIGRATION OUTPUT (Nift, changes over time):
    <absolute path>

Never point parity comparison at MIGRATION OUTPUT on both sides.

## Upstream nondeterminism classification

- [ ] byte deterministic
- [ ] semantic deterministic
- [ ] nondeterministic but bounded/understood (describe)
- [ ] unresolved

## Baseline measurements

- Upstream build time (method, median/range):
- Upstream peak RSS:
- Environment / hardware:
