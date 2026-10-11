"""One-time acquisition of pinned maintained assets; never a routine build step."""
from pathlib import Path
import argparse,hashlib,io,json,re,shutil,tarfile,urllib.request
project=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle-dir',type=Path,help='Use already-acquired bundle parts, without network access')
parser.add_argument('--cache',type=Path,default=Path.home()/'.cache/nift-spacex-assets')
args=parser.parse_args();manifest=json.loads((project/'asset-manifest.json').read_text())
cache=args.cache/manifest['identity'];cache.mkdir(parents=True,exist_ok=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
objects=cache/'objects';objects.mkdir(exist_ok=True)
needed={row['sha256']:row['bytes'] for row in manifest['files']}
missing=[key for key,size in needed.items() if not (objects/key).exists() or (objects/key).stat().st_size!=size or sha(objects/key)!=key]
if missing:
 parts=[]
 for part in manifest['parts']:
  assert Path(part['name']).name==part['name']
  target=(args.bundle_dir or cache)/part['name']
  if not target.exists():
   if args.bundle_dir:raise SystemExit('Missing local bundle part: '+str(target))
   temporary=target.with_suffix('.pending')
   with urllib.request.urlopen(part['url']) as response,temporary.open('wb') as output:shutil.copyfileobj(response,output,1024*1024)
   temporary.rename(target)
  if target.stat().st_size!=part['bytes'] or sha(target)!=part['sha256']:raise SystemExit('Bundle verification failed: '+str(target))
  parts.append(target)
 class Joined:
  def __init__(self):self.index=0;self.current=parts[0].open('rb')
  def read(self,n):
   chunks=[];remaining=n
   while remaining:
    data=self.current.read(remaining)
    if data:chunks.append(data);remaining-=len(data);continue
    self.current.close();self.index+=1
    if self.index==len(parts):break
    self.current=parts[self.index].open('rb')
   return b''.join(chunks)
  def close(self):self.current.close()
 stream=Joined()
 try:
  with tarfile.open(fileobj=stream,mode='r|') as archive:
   for member in archive:
    if not member.isfile() or not re.fullmatch('objects/[a-f0-9]{64}',member.name):raise SystemExit('Unexpected bundle entry')
    key=member.name.split('/')[1]
    if key not in needed or member.size!=needed[key]:raise SystemExit('Unexpected object size or identity')
    target=objects/key;temporary=target.with_suffix('.pending');h=hashlib.sha256()
    with archive.extractfile(member) as source,temporary.open('wb') as output:
     for chunk in iter(lambda:source.read(1024*1024),b''):h.update(chunk);output.write(chunk)
    if h.hexdigest()!=key:raise SystemExit('Object hash verification failed')
    temporary.chmod(0o444);temporary.replace(target)
 finally:stream.close()
for row in manifest['files']:
 destination=project/row['path'];destination.resolve().relative_to(project.resolve())
 source=objects/row['sha256']
 if not source.exists():raise SystemExit('Missing verified object: '+row['sha256'])
 if destination.exists():
  if sha(destination)!=row['sha256']:raise SystemExit('Maintained asset has local changes; not overwritten: '+row['path'])
  continue
 destination.parent.mkdir(parents=True,exist_ok=True)
 # Independent writable maintained files: editing one project cannot mutate the cache or its sibling.
 shutil.copyfile(source,destination);destination.chmod(0o644)
print('Verified maintained assets:',len(manifest['files']))
