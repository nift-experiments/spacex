"""Compare maintained component text/values to the exact public capture per state."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';rows=json.loads((H/'investigation/evidence/tab-state-recovery.json').read_text());checks=[]
def text(root):return re.sub(r'\s+',' ',BeautifulSoup(str(root),'html.parser').get_text(' ',strip=True)).strip()
for row in rows:
 reference=BeautifulSoup(json.loads((W/'spacex-baseline/browser-captures'/row['capture']).read_text())['html'],'html.parser')
 plan=next(p for p in json.loads((H/'investigation/evidence/tab-state-plan.json').read_text()) if p['route']==row['route'] and p['route'].replace('/','-')+'-'+p['key']==row['family'])
 expected=next(t for t in reference.select('metric-tile') if [b.get_text(' ',strip=True) for b in t.select('[role=tab]')]==plan['labels'])
 for project in (H,A):
  page=BeautifulSoup((project/'public'/row['route']/'index.html').read_text(),'html.parser');template=next(t for t in page.select('template[data-native-state-template]') if t['data-native-state-template']==row['family'] and t['data-native-state-value']==row['state']);actual=template.find('metric-tile');valid=text(expected)==text(actual);checks.append({'project':project.name,'family':row['family'],'state':row['state'],'textAndValuesMatchReference':valid})
report={'scope':'Normalized maintained text and metric values; visual/interaction parity is separately required','checks':checks,'allPassed':all(x['textAndValuesMatchReference'] for x in checks),'browserParityAccepted':False}
for p in (H,A):(p/'investigation/evidence/tab-content-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print('Real-corpus state comparisons:',len(checks),'passed:',sum(x['textAndValuesMatchReference'] for x in checks))
if not report['allPassed']:raise SystemExit('Component content mismatch')
