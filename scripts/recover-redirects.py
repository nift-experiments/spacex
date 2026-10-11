"""One-time recovery of delivered route redirects, including inherited CMS 404s."""
from pathlib import Path
import hashlib, json
W = Path(__file__).resolve().parents[2]
R = W / 'spacex-baseline'
declarations = json.loads((R / 'public-route-declarations.json').read_text())['routes']
redirects = []
for row in declarations:
    if row.get('redirectTo') and not row['wildcard']:
        route = ('sites/' if row['bundle'].startswith('6543.') else '') + row['path']
        redirects.append({'route': route, 'target': row['redirectTo'].strip('/') + '/',
                          'reason': 'Delivered client route redirect', 'bundle': row['bundle']})
gaps = json.loads((W / 'spacex/investigation/evidence/mission-recovery.json').read_text())['gaps']
components = json.loads((R / 'component-inventory.json').read_text())['components']
mission_bundle = next(row['file'] for row in components if row['selector'] == 'launch-detail-page')
mission_code = (R / 'capture/www.spacex.com' / mission_bundle).read_text()
assert 'this._router.navigate(["/launches"])' in mission_code
for row in gaps:
    if row.get('status') == 404:
        redirects.append({'route': row['route'].strip('/'), 'target': 'launches/',
                          'reason': 'Inherited CMS 404; delivered mission error handler redirects to launches',
                          'bundle': mission_bundle,
                          'bundleSha256': hashlib.sha256(mission_code.encode()).hexdigest()})
for row in declarations:
    if row['path'] == 'legal' and row.get('externalUrl'):
        redirects.append({'route': 'legal', 'target': row['externalUrl'],
                          'external': True, 'reason': 'Delivered external navigation boundary', 'bundle': row['bundle']})

for project in [W / 'spacex', W / 'spacex-agent']:
    path = project / '.nift/tracked.json'
    registry = json.loads(path.read_text())
    entries = {row['name']: row for row in registry['tracked']}
    for row in redirects:
        name = row['route'] + '/'
        target = row['target'] if row.get('external') else "@path('" + row['target'] + "')"
        source = project / 'content' / name / 'index.html'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                          '<meta name="viewport" content="width=device-width,initial-scale=1">'
                          '<title>SpaceX</title><meta http-equiv="refresh" content="0;url=' + target + '">'
                          '</head><body><a href="' + target + '">Continue</a>'
                          '<script>location.replace("' + target + '")</script></body></html>\n')
        entries[name] = {'name': name, 'title': 'SpaceX', 'template': 'templates/raw.html'}
    registry['tracked'] = list(entries.values())
    path.write_text(json.dumps(registry, indent=2) + '\n')
    (project / 'investigation/evidence/redirect-recovery.json').write_text(json.dumps(redirects, indent=2) + '\n')
print('Recovered redirect routes:', len(redirects))
