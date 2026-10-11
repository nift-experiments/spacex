# Accepted media scope

Offline-preserved: HTML, CSS, JS, images, SVG, fonts, and all media required for captured visual/playback states. Background video must remain video. HLS manifests and required segment subsets must be captured where practical; playback-only classification requires browser evidence.

Remote-referenced: large download/archive-only MP4 renditions. Preserve canonical URLs, visible controls, target/download semantics, page relationships, and captured HEAD metadata. No offline byte preservation claim applies to this class.

Heavy frozen-reference media lives outside both repositories. Routine builds do not fetch live assets. Local maintained asset references use @path.

Scope decision accepted by the user on 2026-10-11. The former full-catalogue storage gate is resolved. S1 remains incomplete pending runtime-media closure and interaction reconciliation.
