# Known differences and remaining parity work

No final parity claim is made. These are open verification/implementation items, not accepted regressions.

| Area | Classification | Current status |
| --- | --- | --- |
| Large download-only MP4 catalogue | Approved preservation scope | Canonical URLs and headers retained; complete bytes are not mirrored. |
| Playback streams | Bounded offline reference | Captured initial segments remain local; uncaptured tails retain canonical public URLs. Full-stream offline archival is not claimed. |
| Private form submissions | Private service boundary | Public UI and confirmation routes recovered; no CAPTCHA success, credentials, real submissions or fabricated backend success. |
| Form conditional fields and validation | Open behavioral parity | Basic native fields, checkboxes, radios and contact/website conditions work; full conditional/validation matrix remains open. |
| Mission gallery, watch, crew, tracker | Open behavioral parity | Source-backed pages are present; remaining controllers and browser states require closure. |
| Marketing tabs and carousels | Open behavioral parity | Native carousel foundation exists; complete family/state coverage remains open. |
| Responsive layout/media | Open visual parity | Desktop source capture exists; viewport matrix and asset switching remain open. |
| Legacy links and malformed public content | Reconciliation pending | Whole-publication audit found 30 missing local destinations; classify original behavior before changing them. |
| External YouTube/service embeds | External service boundary | Original public URLs preserved; offline CSP blocks third-party activity. Embedded playback is not represented as an offline preservation claim. |
| HEVC homepage clip | Browser/codec qualification | Original bytes retained; this IAB cannot decode one clip. No poster/transcode substitution. |
