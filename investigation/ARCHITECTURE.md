# Authored recovery architecture

Recover public sections into small page-family data: headings/body/CTA, local media identity, alignment, gradient/theme and animation options. Shared Nift page/head/navigation/footer and section partials compose maintained data and HTML prose. Use Markdown only where it adds a useful prose authoring model. Readable CSS/vanilla JS own interaction.

Normal publication is `nift build`; static preview is `python3 -m http.server --directory public`. Assets have one maintained home under public/assets, or an explicit pinned maintained-media store if large-file limits require it. No downloads or copying at normal build/preview startup. Use @path for all project-local links, image/video/poster/source URLs, CSS/JS and fonts where Nift renders references. CSS/JS-generated URL handling must retain an explicit path-resolved configuration or be placed relative to its owned static asset location; do not invent root-path assumptions.

No Angular application/source architecture is recreated. No giant intermediate shell tree or custom Node publisher. Any retained animation/runtime dependency requires a recorded observable behavior justification.

## Portable maintained assets

Both projects pin the same asset-manifest.json and shared content-addressed release bundle. scripts/setup-assets.py is an explicit one-time acquisition command, outside normal builds and preview startup. It validates bundle parts and individual object hashes, then creates independent writable publication assets. The canonical bundle exists outside both working trees; no large media enters source Git history. Locally edited assets are not overwritten.

## Player and form boundaries

Media controls use vanilla JavaScript. Native HLS is preferred; pinned vendored HLS.js 1.7.3 is loaded only where native HLS is unavailable. Internal library, stream, poster and playlist URLs are resolved by Nift @path. Playlist durations derive from verified public MP4 metadata and follow the public timespan rounding behavior. The authored model maintains playlist JSON and templates; the agent model maintains rendered playlist HTML.

Recovered open form shadow DOM uses native declarative shadow DOM with public CSS, not an Angular application. Vanilla controls handle basic UI behavior. Private submission services are intentionally unavailable, with no synthetic success or actual transmission. Complete form validation parity remains open.
