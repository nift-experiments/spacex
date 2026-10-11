from pathlib import Path
import subprocess,time,json,re,hashlib,shutil,sys
import argparse
parser=argparse.ArgumentParser(description='Serialized production-publication time/RSS campaign; temporarily edits and restores maintained sources.')
parser.add_argument('project',type=Path);parser.add_argument('output',type=Path)
args=parser.parse_args();project=args.project.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
assert not out.is_relative_to(project), 'Keep benchmark output outside the project'
results=[]
def run(root,scenario,sample,full=False):
 stem=out/f'{root.name}-{scenario}-{sample}';start=time.perf_counter()
 with stem.with_suffix('.log').open('w') as log:
  p=subprocess.run(['/usr/bin/time','-v','-o',str(stem.with_suffix('.time')),'nift','build',*(['--all'] if full else [])],cwd=root,stdout=log,stderr=subprocess.STDOUT)
 if p.returncode: raise RuntimeError(stem.with_suffix('.log').read_text())
 t=stem.with_suffix('.time').read_text(); rss=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',t)[1])/1024
 row={'project':root.name,'scenario':scenario,'sample':sample,'wallSeconds':time.perf_counter()-start,'maxProcessRssMiB':rss,'phase':'Nift composition and dependency evaluation','frontendBundle':False,'backendBuild':False,'command':'nift build'+(' --all' if full else '')}
 results.append(row);(out/'samples.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(row),flush=True)
def build(root):subprocess.run(['nift','build'],cwd=root,stdout=subprocess.DEVNULL,check=True)
def check(root,scenario,changes):
 originals={p:p.read_bytes() for p in changes}
 try:
  for i in range(1,6):
   for p,b in changes.items():p.write_bytes(b)
   run(root,scenario,i)
   for p,b in originals.items():p.write_bytes(b)
   build(root)
 finally:
  for p,b in originals.items():p.write_bytes(b)
  build(root)
for root in [project]:
 name=root.name
 for scenario in ['warm-full','fresh-application-state','unchanged']:
  for i in range(1,6):
   if scenario=='fresh-application-state':shutil.rmtree(root/'.nift/public')
   run(root,scenario,i,scenario=='warm-full')
 auth=root/'data/missions/crew13.json'
 if auth.exists():
  d=json.loads(auth.read_text());d['title']+=' performance probe';ordinary={auth:(json.dumps(d,indent=2)+'\n').encode()}
 else:
  p=root/'content/launches/crew13/index.html';ordinary={p:p.read_bytes().replace(b'Crew-13 Mission',b'Crew-13 Mission performance probe',1)}
 check(root,'ordinary-page-edit',ordinary)
 p=root/'data/home.json' if auth.exists() else root/'content/index.html'
 if auth.exists():
  d=json.loads(p.read_text());d['featured']['title']+=' performance probe';b=(json.dumps(d,indent=2)+'\n').encode()
 else:b=p.read_bytes()+b'\n<!-- homepage performance probe -->\n'
 check(root,'homepage-edit',{p:b})
 for scenario,path in [('shared-layout','templates/footer.html'),('navigation-edit','templates/header.html'),('css-edit','templates/styles.html')]:
  p=root/path;b=p.read_bytes()+ (b'\n<style>.performance-probe{display:none}</style>\n' if scenario=='css-edit' else b'\n<!-- shared performance probe -->\n');check(root,scenario,{p:b})
 p=root/'public/assets/js/site.js';t=root/'templates/template.html';b=p.read_bytes()+b'\n// frontend performance probe\n';digest=hashlib.sha256(b).hexdigest()[:12];template=re.sub(r"(site\.js'\)\?v=)[a-f0-9]+",lambda m:m[1]+digest,t.read_text());assert template!=t.read_text();check(root,'frontend-js-edit',{p:b,t:template.encode()})
 p=root/'public/assets/data/launch-schedule.json';check(root,'media-metadata-edit',{p:p.read_bytes()+b'\n'})
 print('PROJECT RESTORED '+name,flush=True)

for root in [project]:
 name=root.name
 changes={}
 for mission in ['crew12','crew13','crew11']:
  p=root/f'data/missions/{mission}.json'
  if p.exists():
   d=json.loads(p.read_text());d['title']+=' multi-page performance probe';changes[p]=(json.dumps(d,indent=2)+'\n').encode()
  else:
   p=root/f'content/launches/{mission}/index.html';changes[p]=p.read_bytes()+b'\n<!-- multi-page performance probe -->\n'
 check(root,'three-page-edit',changes)
 tracking=(root/'.nift/tracked.json').read_bytes()
 try:
  for i in range(1,6):
   p=root/'content/performance-probe/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<h1>Route lifecycle performance probe</h1>\n')
   subprocess.run(['nift','track','performance-probe/','Performance probe'],cwd=root,stdout=subprocess.DEVNULL,check=True)
   run(root,'route-add',i)
   subprocess.run(['nift','mv','performance-probe/','performance-renamed/'],cwd=root,stdout=subprocess.DEVNULL,check=True)
   run(root,'route-rename',i)
   assert not (root/'public/performance-probe/index.html').exists()
   subprocess.run(['nift','rm','performance-renamed/'],cwd=root,stdout=subprocess.DEVNULL,check=True)
   run(root,'route-delete',i)
   assert not (root/'public/performance-renamed/index.html').exists()
   for p in [root/'content/performance-probe/index.html',root/'content/performance-renamed/index.html']:
    if p.exists():p.unlink()
 finally:
  (root/'.nift/tracked.json').write_bytes(tracking)
  build(root)
 print('LIFECYCLE RESTORED '+name,flush=True)
