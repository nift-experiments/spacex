# SpaceX observable-production migration

This experiment is in progress. It reconstructs the public website, not SpaceX's unavailable private source/build system. Browser parity and final benchmarks remain open.

Acquire the pinned maintained assets once, then build and preview:

```bash
python3 scripts/setup-assets.py
nift build
python3 -m http.server 4173 --bind 127.0.0.1 --directory public
```

Open http://127.0.0.1:4173/ for the actual homepage. Normal builds and preview startup do not download or copy assets. Both variants use the same content-addressed asset bundle hosted by the authored repository; the large downloadable MP4 catalogue keeps its original URLs and is excluded. Each project receives independent writable assets.

For an existing local bundle, use `python3 scripts/setup-assets.py --bundle-dir /path/to/bundle`. Maintained assets with local changes are never overwritten. Pinned base, mobile, responsive, launch-tab, and runtime asset releases are published and remotely hash-verified. The base/mobile/responsive empty-cache network acquisition passed after a recorded temporary-storage failure and cleanup; supplement acquisition is checked separately. See `investigation/STATUS.md` for remaining parity work.

See MIGRATION.md, investigation/BASELINE.md, investigation/PARITY-CONTRACT.md and HANDOVER.md for the method, frozen-reference scope, limitations and remaining work.

Mobile media is supplied by the separately pinned `mobile-asset-manifest.json` supplement. The setup command acquires and verifies the base and all pinned supplements once; ordinary `nift build` commands use maintained assets already present under `public/assets`. Shared acquisition is locked to prevent concurrent projects from writing the same cache objects. The source keeps all internal media paths in `@path`; the native viewport adapter selects the frozen mobile variants. Downloaded transport parts are removed after verified extraction by default; canonical local bundles are retained. `--keep-downloaded-parts` retains network transport copies when needed. Allow disk space for maintained assets, immutable cache objects, and temporary transport parts.
