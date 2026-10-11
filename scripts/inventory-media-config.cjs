// Read only literal media configuration from the frozen public bundles.
// This explicit migration inventory never executes Angular/application code.
const fs=require('fs'),path=require('path'),acorn=require('acorn'),crypto=require('crypto');
const dir=path.resolve(__dirname,'../../spacex-baseline/capture/www.spacex.com');let pairs=[],captions=[],inputs=[];
function field(n,k){return n.properties.find(p=>p.type==='Property'&&(p.key.name||p.key.value)===k)?.value;}
function literal(n){return n?.type==='Literal'?n.value:undefined;}
function walk(n,file){if(!n||typeof n!=='object')return;if(n.type==='ObjectExpression'){
for(const kind of ['image','video']){let desktop=literal(field(n,kind+'Url')),mobile=literal(field(n,'mobile'+kind[0].toUpperCase()+kind.slice(1)+'Url'));if(desktop&&mobile)pairs.push({file,kind,desktop,mobile});}
let caption=literal(field(n,'caption')),tile=field(n,'tile'),sections=tile?.type==='ObjectExpression'?field(tile,'sections'):null;
if(typeof caption==='string'&&sections?.type==='ArrayExpression'){let s=sections.elements[0];if(s?.type==='ObjectExpression')captions.push({file,caption,image:literal(field(s,'imageUrl')),video:literal(field(s,'videoUrl'))});}}
for(let[k,v]of Object.entries(n)){if(['start','end','loc'].includes(k))continue;if(Array.isArray(v))v.forEach(x=>walk(x,file));else if(v&&typeof v==='object')walk(v,file);}}
for(let file of fs.readdirSync(dir).filter(x=>x.endsWith('.js'))){let source=fs.readFileSync(path.join(dir,file));inputs.push({file,sha256:crypto.createHash('sha256').update(source).digest('hex')});walk(acorn.parse(source.toString(),{ecmaVersion:'latest'}),file);}
const report={scope:'Literal public media configuration only; explicit migration inventory, never routine builds',inputs,pairs,captions};
fs.writeFileSync(path.resolve(__dirname,'../investigation/evidence/media-config.json'),JSON.stringify(report,null,2)+'\n');console.log({pairs:pairs.length,captions:captions.length});
