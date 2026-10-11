from pathlib import Path
import hashlib,json,tarfile
PART_BYTES=64*1024*1024
W=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parents[1];rows=[];objects={}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
for folder in ('media','recovered'):
 for f in sorted((P/'public/assets'/folder).rglob('*')):
  if not f.is_file() or f.suffix=='.m3u8':continue
  sha=digest(f);relative=str(f.relative_to(P));other=W/'spacex-agent'/relative
  if other.exists():assert digest(other)==sha,relative
  rows.append({'path':relative,'bytes':f.stat().st_size,'sha256':sha});objects.setdefault(sha,f)
identity=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest();out=W/'spacex-baseline/asset-bundles'/identity;out.mkdir(parents=True,exist_ok=True)
class Parts:
 def __init__(self):self.stream=None;self.number=0;self.size=0;self.paths=[]
 def write(self,data):
  total=len(data)
  while data:
   if not self.stream or self.size==PART_BYTES:
    if self.stream:self.stream.close()
    path=out/f'assets-64m-{self.number:03d}.tar.part';self.number+=1;self.paths.append(path);self.stream=path.open('wb');self.size=0
   n=min(len(data),PART_BYTES-self.size);self.stream.write(data[:n]);self.size+=n;data=data[n:]
  return total
 def close(self):
  if self.stream:self.stream.close()
writer=Parts()
with tarfile.open(fileobj=writer,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
 for sha,f in sorted(objects.items()):
  info=tarfile.TarInfo('objects/'+sha);info.size=f.stat().st_size;info.mode=0o444
  with f.open('rb') as source:archive.addfile(info,source)
writer.close();tag='maintained-assets-'+identity[:16]
manifest={'schema':1,'identity':identity,'scope':'Maintained playback, image and document assets only; download-only MP4 catalogue excluded','releaseRepository':'nift-experiments/spacex','releaseTag':tag,'files':rows,'parts':[{'name':f.name,'bytes':f.stat().st_size,'sha256':digest(f),'url':f'https://github.com/nift-experiments/spacex/releases/download/{tag}/{f.name}'} for f in writer.paths]}
(out/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for name in ('spacex','spacex-agent'):(W/name/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'files':len(rows),'uniqueObjects':len(objects),'publicationBytes':sum(x['bytes'] for x in rows),'bundleBytes':sum(x['bytes'] for x in manifest['parts']),'parts':len(writer.paths),'bundleDirectory':str(out),'releaseTag':tag}),flush=True)
