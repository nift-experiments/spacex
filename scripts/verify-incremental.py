from pathlib import Path
import sys,json,hashlib,subprocess,re,time
root=Path(sys.argv[1]).resolve();report=[]
def command(*args):
 result=subprocess.run(['nift',*args],cwd=root,capture_output=True,text=True)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 return result.stdout
def snapshot():
 return {str(p.relative_to(root/'public')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'public').rglob('*') if p.is_file() and (p.suffix in ['.html','.m3u8'] or '/assets/js/' in str(p) or '/assets/data/' in str(p))}
def check(name,changes):
 originals={p:p.read_bytes() for p in changes}
 before=snapshot()
 try:
  for p,content in changes.items():p.write_bytes(content)
  output=command('build');incremental=snapshot();command('build','--all');forced=snapshot()
  assert incremental==forced,name
  changed=[key for key in incremental if before.get(key)!=incremental[key]]
  report.append({'scenario':name,'incrementalEqualsForcedFull':True,'changedPublicationFiles':len(changed),'changedGeneratedFiles':sum(key.endswith(('.html','.m3u8')) for key in changed),'buildSummary':output[-1200:]})
 finally:
  for p,content in originals.items():p.write_bytes(content)
  command('build')
command('build','--all');original=snapshot();mtimes={p:p.stat().st_mtime_ns for p in (root/'public').rglob('*') if p.is_file() and p.suffix in ['.html','.m3u8']};output=command('build');assert all(p.stat().st_mtime_ns==mtime for p,mtime in mtimes.items());report.append({'scenario':'unchanged','noGeneratedWrites':True,'buildSummary':output[-800:]})
auth=root/'data/missions/crew13.json'
if auth.exists():
 data=json.loads(auth.read_text());data['title']+=' lifecycle probe';check('ordinary-content',{auth:(json.dumps(data,indent=2)+'\n').encode()})
else:
 p=root/'content/launches/crew13/index.html';check('ordinary-content',{p:p.read_bytes().replace(b'Crew-13 Mission',b'Crew-13 Mission lifecycle probe',1)})
for scenario,path in [('shared-layout','templates/footer.html'),('shared-navigation','templates/header.html'),('shared-css','templates/styles.html')]:
 p=root/path;check(scenario,{p:p.read_bytes()+b'\n<!-- lifecycle probe -->\n'})
p=root/'public/assets/js/site.js';t=root/'templates/template.html';changed=p.read_bytes()+b'\n// lifecycle frontend probe\n';digest=hashlib.sha256(changed).hexdigest()[:12];template=re.sub(r"(site\.js'\)\?v=)[a-f0-9]+",lambda m:m[1]+digest,t.read_text());check('frontend-js-with-cache-key',{p:changed,t:template.encode()})
p=root/'public/assets/data/launch-schedule.json';check('maintained-media-metadata',{p:p.read_bytes()+b'\n'})
tracking=(root/'.nift/tracked.json').read_bytes();p=root/'content/lifecycle-probe/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<h1>Lifecycle probe</h1>\n')
try:
 command('track','lifecycle-probe/','Lifecycle probe');command('build');assert (root/'public/lifecycle-probe/index.html').is_file();inc=snapshot();command('build','--all');assert inc==snapshot();report.append({'scenario':'route-add','incrementalEqualsForcedFull':True})
 command('mv','lifecycle-probe/','lifecycle-renamed/');command('build');assert not (root/'public/lifecycle-probe/index.html').exists();assert (root/'public/lifecycle-renamed/index.html').is_file();inc=snapshot();command('build','--all');assert inc==snapshot();report.append({'scenario':'route-rename','incrementalEqualsForcedFull':True,'oldOutputAbsent':True})
 command('rm','lifecycle-renamed/');command('build');assert not (root/'public/lifecycle-renamed/index.html').exists();inc=snapshot();command('build','--all');assert inc==snapshot();report.append({'scenario':'route-delete','incrementalEqualsForcedFull':True,'removedOutputAbsent':True})
finally:
 (root/'.nift/tracked.json').write_bytes(tracking)
 for path in [root/'content/lifecycle-probe/index.html',root/'content/lifecycle-renamed/index.html']:
  if path.exists():path.unlink()
 command('build','--all')
assert original==snapshot(),'restored publication differs'
(root.parent/(root.name+'-incremental.json')).write_text(json.dumps({'project':root.name,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'checks':report,'restoredPublicationExact':True,'finalParityAccepted':False},indent=2)+'\n')
print(json.dumps({'project':root.name,'checks':len(report),'restoredPublicationExact':True}))
