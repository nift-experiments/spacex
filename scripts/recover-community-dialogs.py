"""Recover the two observed Mid-South dialogs and their exact public choices."""
from pathlib import Path
from bs4 import BeautifulSoup,Comment
import json,copy,hashlib
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline/browser-captures';rows=[]
def captured(ending):
 p=next(B.glob('*'+ending+'*'));return BeautifulSoup(json.loads(p.read_text())['html'],'html.parser'),p
for kind,ending,title,menus in [('partner','f005c5d5826e','partner-dialog-title',['99dac9bd9cab','5a5298e01205','19bc6b6591de']),('feedback','da792cec0899','newsletter-feedback-dialog-title',['517c810ce2e5','a8a31bbacd0c'])]:
 dom,p=captured(ending);root=dom.select_one('[aria-labelledby="'+title+'"]').parent;root['data-community-dialog']=kind
 groups=root.select('.partner-ms')
 for index,(group,cap) in enumerate(zip(groups,menus)):
  reference,file=captured(cap);panel=reference.select_one('[aria-labelledby="'+title+'"]');menu=copy.deepcopy(panel.select_one('.partner-ms.is-open [role=listbox]'));assert menu
  menu['hidden']='';menu['id']='native-'+kind+'-choices-'+str(index);group['data-community-choice']='';group['data-multiple']='true' if kind=='partner' and index<2 else 'false';group['data-required-choice']='true'
  trigger=group.select_one('button');trigger['aria-controls']=menu['id'];trigger['aria-expanded']='false';trigger['aria-label']=group.parent.select_one('.partner-form__label').get_text(' ',strip=True).replace('*','').strip();group['data-placeholder']=trigger.get_text(' ',strip=True)
  for option in menu.select('[role=option]'):option['aria-selected']='true' if 'is-on' in option.get('class',[]) else 'false'
  group.append(menu);rows.append({'dialog':kind,'choicesCapture':file.name,'choices':len(menu.select('[role=option]'))})
 for comment in root.find_all(string=lambda x:isinstance(x,Comment)):comment.extract()
 for field in root.select('label'):
  control=field.select_one('input,textarea')
  if control:control['aria-label']=field.select_one('.partner-form__label').get_text(' ',strip=True).replace('*','').strip()
 if kind=='partner':
  other,other_file=captured('5a713ba4f6f6');extra=next(x for x in other.select('.partner-form__field') if x.select_one('.partner-form__label') and x.select_one('.partner-form__label').get_text(' ',strip=True)=='Please specify');extra['hidden']='';extra['data-other-organization']='';extra.select_one('input')['disabled']='';extra.select_one('input')['aria-label']='Please specify'
  for comment in extra.find_all(string=lambda x:isinstance(x,Comment)):comment.extract()
  field=next(x for x in root.select('.partner-form__field') if x.select_one('.partner-form__label') and x.select_one('.partner-form__label').get_text(' ',strip=True)=='Organization type');field.insert_after(extra)
 fragment=str(root)
 for name in ['spacex','spacex-agent']:
  project=W/name;path=project/'content/Mid-South/index.html';source=path.read_text();d=BeautifulSoup(source,'html.parser');selector='#partners button' if kind=='partner' else '#newsletter-feedback button';trigger=d.select_one(selector);assert trigger;old=str(trigger);trigger['data-community-open']=kind;assert old in source;source=source.replace(old,str(trigger),1)
  if name=='spacex':
   relative='templates/dialogs/'+kind+'.html';out=project/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(fragment+'\n');body="@input('"+relative+"')"
  else:body=fragment
  assert 'data-community-template="'+kind+'"' not in source,'Explicit recipe already applied'
  source+='\n<template data-community-template="'+kind+'">'+body+'</template>\n';path.write_text(source)
for name in ['spacex','spacex-agent']:
 project=W/name;path=project/'content/Mid-South/index.html';source=path.read_text();d=BeautifulSoup(source,'html.parser');form=d.select_one('.memphis-close__form');old=str(form);form['data-newsletter-form']='';form.select_one('input')['aria-label']='Your email address';path.write_text(source.replace(old,str(form),1))
 (project/'investigation/evidence/community-dialogs.json').write_text(json.dumps({'choices':rows,'service':'Explicitly unavailable; no private requests or simulated success','validationParity':'Native captured required fields; complete rule comparison remains open','browserParityAccepted':False},indent=2)+'\n')
print('Recovered partner and feedback dialogs with',sum(r['choices'] for r in rows),'captured choices')
