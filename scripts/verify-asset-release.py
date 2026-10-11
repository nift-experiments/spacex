"""Read-only verification of GitHub release SHA-256 digests against pinned parts."""
from pathlib import Path
import argparse,json,subprocess,hashlib
p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parents[1]/'asset-manifest.json');p.add_argument('--require-complete',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.manifest.read_text())
tag=m['releaseTag'];repo=m['releaseRepository'];result=subprocess.run(['gh','api',f'repos/{repo}/releases/tags/{tag}'],capture_output=True,text=True,check=True,timeout=60);release=json.loads(result.stdout);remote={r['name']:r for r in release['assets']};rows=[]
expected=[{'name':'asset-manifest.json','bytes':a.manifest.stat().st_size,'sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest()},*m['parts']]
for part in expected:
 r=remote.get(part['name']);valid=bool(r and r['state']=='uploaded' and r['size']==part['bytes'] and r.get('digest')=='sha256:'+part['sha256']);rows.append({'name':part['name'],'verified':valid,'expectedSha256':part['sha256'],'remoteDigest':r.get('digest') if r else None,'remoteBytes':r.get('size') if r else None})
report={'repository':repo,'tag':tag,'releaseId':release['id'],'identity':m['identity'],'verification':'GitHub upload digest and byte count against locally pinned manifest; fresh acquisition is separately required','allVerified':all(r['verified'] for r in rows),'assets':rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('Verified',sum(r['verified'] for r in rows),'of',len(rows))
if a.require_complete and not report['allVerified']:raise SystemExit('Release is incomplete or has mismatched assets')
