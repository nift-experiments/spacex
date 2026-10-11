// Inspect publicly delivered compiled configuration; never execute the application.
const fs=require('fs'), path=require('path'), acorn=require('acorn'), crypto=require('crypto');
const root=path.resolve(__dirname,'../../spacex-baseline'), dir=path.join(root,'capture/www.spacex.com');
const results=[];
function prop(n,k){return n.properties.find(p=>p.type==='Property'&&(p.key.name||p.key.value)===k)?.value;}
function walk(n,file){if(!n||typeof n!=='object')return;
 if(n.type==='ObjectExpression'){
  const selector=prop(n,'selectors'),styles=prop(n,'styles');
  if(selector?.type==='ArrayExpression'&&styles?.type==='ArrayExpression'){
   const name=selector.elements[0]?.elements?.[0]?.value;
   if(typeof name==='string'){const css=styles.elements.filter(x=>x?.type==='Literal'&&typeof x.value==='string').map(x=>x.value);results.push({selector:name,file,styles:css,styleSha256:crypto.createHash('sha256').update(css.join('\n')).digest('hex'),compiledTemplatePresent:!!prop(n,'template')});}
  }
 }
 for(const [k,v] of Object.entries(n)){if(['start','end','loc'].includes(k))continue;if(Array.isArray(v))v.forEach(x=>walk(x,file));else if(v&&typeof v==='object')walk(v,file);}
}
for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.js')))walk(acorn.parse(fs.readFileSync(path.join(dir,file),'utf8'),{ecmaVersion:'latest'}),file);
fs.writeFileSync(path.join(root,'component-inventory.json'),JSON.stringify({scope:'Observed public compiled configuration, not recovered private source; no application code executed',components:results},null,2)+'\n');
console.log('Public component/style configurations:',results.length);
