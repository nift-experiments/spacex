"""Explicit maintenance: package frozen mobile media missing from the base release."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,tarfile,shutil
W=Path(__file__).resolve().parents[2];P=W/'spacex';B=W/'spacex-baseline';rows=[];objects={}
config=json.loads((P/'investigation/evidence/media-config.json').read_text());base={r['path'] for r in json.loads((P/'asset-manifest.json').read_text())['files']}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
paths=set()
for item in config['pairs']:
 u=urlsplit(item['mobile']);rel=(u.netloc or 'www.spacex.com')+'/'+u.path.lstrip('/');target='public/assets/recovered/'+rel
 if target in base:continue
 paths.add((rel,target))
for rel,target in sorted(paths):
 source=B/'capture'/rel;receipt=Path(str(source)+'.receipt.json')
 if not source.is_file() or not receipt.is_file():raise SystemExit('Missing frozen mobile asset: '+rel)
 r=json.loads(receipt.read_text());key=digest(source)
 if not r['transferComplete'] or r['status'] not in ('200','206') or key!=r['sha256']:raise SystemExit('Invalid mobile capture: '+rel)
 rows.append({'path':target,'bytes':source.stat().st_size,'sha256':key});objects.setdefault(key,source)
 for name in ('spacex','spacex-agent'):
  destination=W/name/target
  if destination.exists():assert digest(destination)==key
  else:destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
identity=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest();out=B/'asset-bundles'/identity;out.mkdir(parents=True,exist_ok=True)
class Parts:
 def __init__(self):self.stream=None;self.number=0;self.size=0;self.paths=[]
 def write(self,data):
  total=len(data)
  while data:
   if not self.stream or self.size==64*1024*1024:
    if self.stream:self.stream.close()
    p=out/f'mobile-64m-{self.number:03d}.tar.part';self.number+=1;self.paths.append(p);self.stream=p.open('wb');self.size=0
   n=min(len(data),64*1024*1024-self.size);self.stream.write(data[:n]);self.size+=n;data=data[n:]
  return total
 def close(self):
  if self.stream:self.stream.close()
w=Parts()
with tarfile.open(fileobj=w,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
 for key,p in sorted(objects.items()):
  info=tarfile.TarInfo('objects/'+key);info.size=p.stat().st_size;info.mode=0o444
  with p.open('rb') as source:archive.addfile(info,source)
w.close();tag='maintained-mobile-'+identity[:16]
m={'schema':1,'identity':identity,'scope':'Frozen playback and image mobile variants; supplement to unchanged base bundle','releaseRepository':'nift-experiments/spacex','releaseTag':tag,'files':rows,'parts':[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p),'url':f'https://github.com/nift-experiments/spacex/releases/download/{tag}/{p.name}'} for p in w.paths]}
(out/'asset-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for name in ('spacex','spacex-agent'):(W/name/'mobile-asset-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'files':len(rows),'publicationBytes':sum(r['bytes'] for r in rows),'parts':len(w.paths),'bundleDirectory':str(out),'releaseTag':tag}))
