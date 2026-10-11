"""Restore observed unscoped public CSS at its three actual page families."""
from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';plans=json.loads((W/'spacex/investigation/evidence/page-family-recovery.json').read_text())
rows=[];canonical=None
for route in ['sites','sites/starbase-tx','Mid-South']:
 capture=next(B.glob('browser-captures/*ff61715bb22c*')) if route=='Mid-South' else B/'browser-captures'/next(p['capture'] for p in plans if p['route'].strip('/')==route)
 record=json.loads(capture.read_text());styles=[s for s in record['styles'] if '.page--' in s]
 assert len(styles)==2 and all('url(' not in s for s in styles)
 hashes=[hashlib.sha256(s.encode()).hexdigest() for s in styles]
 if canonical is None:canonical=styles
 assert styles==canonical,'Different public styles must be preserved separately'
 rows.append({'route':route,'capture':capture.name,'stylesSha256':hashes})
for name in ['spacex','spacex-agent']:
 project=W/name;(project/'templates/unscoped-site-styles.html').write_text('<style>\n'+'\n'.join(canonical).replace('@','\\@')+'\n</style>\n')
 for row in rows:(project/'templates/families'/(row['route'].replace('/','-')+'.html')).write_text("@input('templates/unscoped-site-styles.html')\n"+("@input('templates/community-styles.html')\n" if row['route']=='Mid-South' and (project/'templates/community-styles.html').exists() else ''))
 (project/'investigation/evidence/unscoped-site-styles.json').write_text(json.dumps({'reason':'Public unscoped page styles omitted by scoped-only migration recipe','families':rows,'maintainedCopiesPerProject':1,'browserParityAccepted':False},indent=2)+'\n')
print('Recovered exact shared CSS for',len(rows),'observed families')
