from pathlib import Path
import re,posixpath,json,subprocess,argparse
options=argparse.ArgumentParser(description='Explicit one-time rendered-source recovery, never a build step')
options.add_argument('--missions',nargs='+',required=True)
args=options.parse_args()
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';d=json.loads((H/'investigation/evidence/mission-recovery.json').read_text())
tracked={x['name'] for x in json.loads((A/'.nift/tracked.json').read_text())['tracked']}
for row in d['recovered']:
 if row['name'].strip('/').split('/')[-1] not in args.missions:continue
 name=row['name'];page=H/'public'/name/'index.html';document=page.read_text();main=re.search(r'<main>(.*?)</main>',document,re.S).group(1)
 main=re.sub(r'^\s*<style>.*?</style>',"@input('templates/mission-styles.html')",main,flags=re.S)
 def internal(m):
  field,value=m.group(1),m.group(2)
  if not value or (re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',value.lstrip()) or value.startswith('#')):return m.group(0)
  target,sep,fragment=value.partition('#');target=posixpath.normpath(posixpath.join('public',name,target))
  if not target.startswith('public/'):raise ValueError('unexpected publication path '+target+' route='+name+' value='+value)
  binding=target if target.startswith('public/assets/') else target.removeprefix('public/').rstrip('/')+'/'
  if not binding.startswith('public/') and binding not in tracked:binding='public/'+binding
  if binding.startswith('public/') and not binding.startswith('public/assets/'):(A/binding).mkdir(parents=True,exist_ok=True)
  return field+'="@path(\''+binding+'\')'+('#'+fragment if sep else '')+'"'
 main=re.sub(r'(href|src|srcset|poster|data-mobile)="([^"]*)"',internal,main)
 p=A/'content'/name/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(main+'\n')
result=subprocess.run(['nift','build','--repair'],cwd=A,capture_output=True,text=True);print(result.stdout[-800:]);print(result.stderr[:1500]);print('Agent maintained rendered mission pages',len(args.missions),'exit',result.returncode)
