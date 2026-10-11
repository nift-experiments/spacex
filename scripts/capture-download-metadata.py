"""Capture small MP4 metadata ranges for playlist duration labels, not payloads.

These files remain remote-reference downloads. Range receipts never imply
offline preservation of the complete MP4 or its playback.
"""
from pathlib import Path
import concurrent.futures, hashlib, json, re, subprocess
R = Path(__file__).resolve().parents[2] / 'spacex-baseline'
manifest = json.loads((R / 'media-preservation-manifest.json').read_text())
selected = [item for item in manifest if item['preservationMode'] == 'remote-reference'
            and any(relation['mediaRole'] == 'hdLink' for relation in item['relationships'])]

def capture(item):
    total = item['contentLength']
    if not total:
        return {'url': item['url'], 'complete': False, 'error': 'Missing content length'}
    identifier = hashlib.sha256(item['url'].encode()).hexdigest()
    directory = R / 'download-metadata' / identifier
    directory.mkdir(parents=True, exist_ok=True)
    ranges = []
    for name, start, end in [('head', 0, min(total - 1, 1048575)),
                             ('tail', max(0, total - 2097152), total - 1)]:
        target = directory / (name + '.bin')
        headers = directory / (name + '.headers')
        result = subprocess.run(['curl', '-sSL', '--max-time', '45', '--retry', '2',
                                 '--range', f'{start}-{end}', '-D', str(headers),
                                 item['url'], '-o', str(target)], capture_output=True, text=True)
        captured = headers.read_text() if headers.exists() else ''
        matches = re.findall(r'content-range:\s*bytes (\d+)-(\d+)/(\d+)', captured, re.I)
        complete = result.returncode == 0 and matches and tuple(map(int, matches[-1])) == (start, end, total)
        complete = bool(complete and target.stat().st_size == end - start + 1)
        ranges.append({'start': start, 'end': end, 'complete': complete,
                       'path': str(target.relative_to(R)),
                       'sha256': hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None})
    print(item['filename'], all(part['complete'] for part in ranges), flush=True)
    return {'url': item['url'], 'contentLength': total, 'contentType': item['contentType'],
            'etag': item['etag'], 'preservationMode': 'remote-reference',
            'scope': 'Bounded metadata ranges only; no MP4 playback or complete-file preservation claim',
            'ranges': ranges}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(capture, selected))
(R / 'download-metadata-ranges.json').write_text(json.dumps(records, indent=2) + '\n')
