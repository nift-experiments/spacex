// Public-output inventory only: read compiled route declarations without executing them.
const fs=require('fs'),path=require('path'),acorn=require('acorn');
const R=path.resolve(__dirname,'../../spacex-baseline'), C=path.join(R,'capture');
const files=[path.join(C,'main.38aaaafc31bc4ec8.js'),...fs.readdirSync(path.join(C,'www.spacex.com')).filter(x=>x.endsWith('.js')).map(x=>path.join(C,'www.spacex.com',x))];
const routes=[];
function prop(n,k){return n.properties.find(p=>p.type==='Property'&&(p.key.name||p.key.value)===k)?.value;}
for(const f of files){let source=fs.readFileSync(f,'utf8');function walk(n){if(!n||typeof n!=='object')return;
 if(n.type==='ObjectExpression'){let route=prop(n,'path');if(route?.type==='Literal'&&typeof route.value==='string'){let load=prop(n,'loadChildren'), redirect=prop(n,'redirectTo'),data=prop(n,'data');routes.push({bundle:path.basename(f),path:route.value,redirectTo:redirect?.value||null,externalUrl:data?.type==='ObjectExpression'?prop(data,'externalUrl')?.value||null:null,lazyModuleRefs:load?[...source.slice(load.start,load.end).matchAll(/\.e\((\d+)\)/g)].map(x=>x[1]):[],wildcard:route.value.includes('*'),parameterized:route.value.includes(':')});}}
 for(const [k,v] of Object.entries(n)){if(['start','end','loc'].includes(k))continue;if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}}
 walk(acorn.parse(source,{ecmaVersion:'latest'}));}
fs.writeFileSync(path.join(R,'public-route-declarations.json'),JSON.stringify({scope:'Public compiled declarations, not private authored source; child paths require parent reconciliation',routes},null,2)+'\n');console.log('Route declarations:',routes.length,'redirects:',routes.filter(x=>x.redirectTo||x.externalUrl).length);
