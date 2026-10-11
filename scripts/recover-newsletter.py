"""Explicit recovery of the observed newsletter UI; no subscription service."""
from pathlib import Path
from bs4 import BeautifulSoup,Comment
import json
W=Path(__file__).resolve().parents[2]
capture=next((W/'spacex-baseline/browser-captures').glob('*bf6b401218c5*'))
d=json.loads(capture.read_text());root=BeautifulSoup(next(r['html'] for r in d['shadowRoots'] if r['tag']=='email-signup'),'html.parser')
form=root.select_one('#signupform');content=form.parent
for comment in content.find_all(string=lambda t:isinstance(t,Comment)):comment.extract()
form.attrs={'data-newsletter-form':'','novalidate':''}
email=form.select_one('input');email.attrs={'type':'email','autocomplete':'email','placeholder':'Your email address','aria-label':'Your email address','required':''}
button=form.select_one('a');button.name='button';button['type']='submit';button.attrs.pop('tabindex',None)
styles=''.join(str(s) for s in root.select('style') if '.email-signup-content' in s.get_text() or '[_ngcontent-jqt-c72]' in s.get_text())
fragment=('<template shadowrootmode="open">'+styles+str(content)+'</template>').replace('@','\\@')
for name in ['spacex','spacex-agent']:
 project=W/name;count=0
 if name=='spacex':(project/'templates/newsletter.html').write_text(fragment+'\n')
 for path in (project/'content').rglob('*.html'):
  old=path.read_text();dom=BeautifulSoup(old,'html.parser');new=old
  for host in dom.select('email-signup'):
   if list(host.children):continue
   literal=str(host);replacement=literal.replace('</email-signup>',("@input('templates/newsletter.html')" if name=='spacex' else fragment)+'</email-signup>')
   new=new.replace(literal,replacement);count+=1
  if new!=old:path.write_text(new)
 (project/'investigation/evidence/newsletter-recovery.json').write_text(json.dumps({'capture':capture.name,'maintainedHosts':count,'service':'Unavailable; never transmits subscription requests','browserParityAccepted':False},indent=2)+'\n')
 print(name,count,'newsletter hosts')
