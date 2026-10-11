# SpaceX observable-production migration

This experiment is in progress. It reconstructs the public website, not SpaceX's unavailable private source/build system. Browser parity and final benchmarks remain open.

Acquire the pinned maintained assets once, then build and preview:

```bash
python3 scripts/setup-assets.py
nift build
python3 -m http.server 4173 --bind 127.0.0.1 --directory public
```

Open http://127.0.0.1:4173/ for the actual homepage. Normal builds and preview startup do not download or copy assets. Both variants use the same content-addressed asset bundle hosted by the authored repository; the large downloadable MP4 catalogue keeps its original URLs and is excluded. Each project receives independent writable assets.

For an existing local bundle, use `python3 scripts/setup-assets.py --bundle-dir /path/to/bundle`. Maintained assets with local changes are never overwritten. Asset publication currently awaits its checkpoint release; see `investigation/STATUS.md`.

See MIGRATION.md, investigation/BASELINE.md, investigation/PARITY-CONTRACT.md and HANDOVER.md for the method, frozen-reference scope, limitations and remaining work.
