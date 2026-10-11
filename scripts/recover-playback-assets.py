"""One-time maintained HLS recovery. Native Nift composes its internal paths.

Captured segment windows are local; uncaptured playback tails retain canonical
URLs. No claim is made that these bounded inputs archive complete streams.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json, re, shutil
W = Path(__file__).resolve().parents[2]
R = W / 'spacex-baseline'
rows = json.loads((R / 'playback-window.json').read_text())['inputs']
known = {row['url']: row for row in rows if row['transferComplete']}
for project in [W / 'spacex', W / 'spacex-agent']:
    tracking = project / '.nift/tracked.json'
    registry = json.loads(tracking.read_text())
    entries = {item['name']: item for item in registry['tracked']}
    (project / 'templates/raw.html').write_text('@content\n')
    for url, row in known.items():
        parsed = urlsplit(url)
        relative = 'assets/recovered/' + parsed.netloc + parsed.path
        original = R / row['path']
        if not parsed.path.endswith('.m3u8'):
            target = project / 'public' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists(): shutil.copy2(original, target)
            continue
        def reference(uri):
            absolute = urljoin(url, uri)
            if absolute not in known: return absolute
            part = urlsplit(absolute)
            destination = 'assets/recovered/' + part.netloc + part.path
            if destination.endswith('.m3u8'): destination = destination.removesuffix('.m3u8')
            else: destination = 'public/' + destination
            return "@path('" + destination + "')"
        lines = []
        for line in original.read_text().splitlines():
            if line.startswith('#'):
                line = re.sub(r'URI="([^"]+)"', lambda match: 'URI="' + reference(match[1]) + '"', line)
            elif line.strip():
                line = reference(line.strip())
            lines.append(line)
        source = project / 'content' / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('\n'.join(lines) + '\n')
        name = relative.removesuffix('.m3u8')
        entries[name] = {'name': name, 'title': Path(parsed.path).name,
                         'content-ext': '.m3u8', 'output-ext': '.m3u8', 'template': 'templates/raw.html'}
    registry['tracked'] = list(entries.values())
    tracking.write_text(json.dumps(registry, indent=2) + '\n')
print('Recovered playback inputs:', len(known), 'including', sum(url.endswith('.m3u8') for url in known), 'native HLS manifests')
