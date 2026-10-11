"""Explicit release maintenance only; never called by a site build."""
from pathlib import Path
import argparse,json,subprocess,time,concurrent.futures,threading
p=argparse.ArgumentParser();p.add_argument('--bundle-dir',type=Path,required=True);a=p.parse_args()
m=json.loads((a.bundle_dir/'asset-manifest.json').read_text());repo=m['releaseRepository'];tag=m['releaseTag']
lock=threading.Lock();progress={};receipt=a.bundle_dir/'upload-progress.json'
def save():
 with lock:
  temp=receipt.with_suffix('.pending');temp.write_text(json.dumps(progress,indent=2)+'\n');temp.replace(receipt)
def upload(part):
 for attempt in range(1,4):
  remote=subprocess.run(['gh','release','view',tag,'--repo',repo,'--json','assets'],capture_output=True,text=True,timeout=60)
  if remote.returncode==0:
   found=next((x for x in json.loads(remote.stdout)['assets'] if x['name']==part['name'] and x['state']=='uploaded' and x['size']==part['bytes']),None)
   if found:
    progress[part['name']]={'state':'uploaded','bytes':found['size'],'url':found['url']};save();return
  try:
   result=subprocess.run(['gh','release','upload',tag,str(a.bundle_dir/part['name']),'--repo',repo,'--clobber'],capture_output=True,text=True,timeout=900)
   progress[part['name']]={'attempt':attempt,'state':'uploaded' if result.returncode==0 else 'retry','message':result.stderr[-500:]};save()
   if result.returncode==0:return
  except subprocess.TimeoutExpired:
   progress[part['name']]={'attempt':attempt,'state':'retry','message':'transfer timeout'};save()
  time.sleep(5*attempt)
 progress[part['name']]['state']='failed';save()
subprocess.run(['gh','release','upload',tag,str(a.bundle_dir/'asset-manifest.json'),'--repo',repo,'--clobber'],check=True,timeout=120)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(upload,m['parts']))
if any(x['state']=='failed' for x in progress.values()):raise SystemExit('Asset upload has failed parts; inspect upload-progress.json and resume explicitly')
print('All parts uploaded; independent remote hash verification remains required',flush=True)
