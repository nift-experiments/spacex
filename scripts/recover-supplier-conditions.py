"""Explicit recovery of observed public supplier repeat-field structures."""
from pathlib import Path
from bs4 import BeautifulSoup,Comment
import json,hashlib,copy
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';capture=W/'spacex-baseline/browser-captures/supplier-submit.1280x720.9ba888005c6a.json';r=json.loads(capture.read_text());dom=BeautifulSoup(next(x['html'] for x in r['shadowRoots'] if x['tag']=='supplier-submit-page'),'html.parser')
naics=dom.find(id='mat-input-0').find_parent('mat-form-field').parent
csi=dom.find(id='csi-sub-code').parent.parent.parent
for kind,row in [('naics',naics),('csi',csi)]:
 row['data-repeat-row']=kind
 for tag in [row,*row.find_all(True)]:
  for attr in list(tag.attrs):
   if attr.startswith(('_nghost-','_ngcontent-')):tag['data-sx-host' if attr.startswith('_nghost') else 'data-sx']='delete-svg';del tag[attr]
  if tag.name=='button':tag['type']='button';tag['data-remove-code']=kind
  if tag.name in ('input','select'):tag['data-code-field']=kind
 for comment in row.find_all(string=lambda x:isinstance(x,Comment)):comment.extract()
for project in (H,A):
 path=project/'content/supplier/submit/index.html';source=path.read_text()
 if 'data-csi-condition' in source:raise SystemExit('Conditions already maintained; edit sources directly rather than overwriting them')
 s=BeautifulSoup(source,'html.parser');field=s.select_one('[data-field="naicsCodes"]');wrapper=next(x for x in field.find_next_siblings() if x.name=='div' and x.has_attr('hidden'))
 old=str(wrapper);assert old in source;wrapper['data-naics-condition']='yes';box=wrapper.select_one('.col-span-1');listing=s.new_tag('div',attrs={'data-repeat-list':'naics'});listing.append(copy.deepcopy(naics));box.insert(0,listing);add=next(b for b in box.select('button') if 'Add NAICS Code' in str(b));add['type']='button';add['data-add-code']='naics'
 for kind,row in [('naics',naics),('csi',csi)]:
  template=s.new_tag('template',attrs={'data-repeat-template':kind})
  if project==H:
   rel='content/forms/'+kind+'-row.html';out=project/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(str(row)+'\n');template.append("@input('"+rel+"')")
  else:template.append(copy.deepcopy(row))
  wrapper.append(template)
 source=source.replace(old,str(wrapper),1)
 # The public No branch is separate and required.
 spec=s.select('[data-field="specializationDescription"]')[-1].find_parent('div',class_='epdk-form-field');old=str(spec);assert old in source;spec['data-naics-condition']='no';spec.select_one('textarea')['id']='industrySpecializations';spec.select_one('label')['for']='industrySpecializations';source=source.replace(old,str(spec),1)
 group=s.select_one('[data-field="providesConstructionServices"]');old=str(group);assert old in source
 block=s.new_tag('div',attrs={'data-csi-condition':'','hidden':''});heading=copy.deepcopy(csi.previous_sibling);block.append(heading);block.append(s.new_tag('div',attrs={'data-repeat-list':'csi'}));add=copy.deepcopy(next(b for b in dom.select('button') if b.get_text(' ',strip=True)=='Add CSI Code').parent);add.select_one('button')['type']='button';add.select_one('button')['data-add-code']='csi';block.append(add);source=source.replace(old,old+str(block),1);source=source.replace('<button class="mat-focus-indicator spacex-fab-button', '<button type="submit" class="mat-focus-indicator spacex-fab-button',1);path.write_text(source)
 evidence={'capture':capture.name,'sha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'naicsInitialRows':1,'csiInitialRows':0,'csiOptions':len(csi.select('option')),'privateSubmission':'unavailable, not exercised','browserParityAccepted':False};(project/'investigation/evidence/supplier-condition-recovery.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('Recovered public NAICS and CSI repeat structures')
