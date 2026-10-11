/* Native public careers search/filter boundary; maintained job HTML, no CMS build stage. */
(() => {
  const root=document.querySelector('[data-careers-jobs]');
  const careerSearch=document.querySelector('[data-sx-host="career-search-tile"]');
  if(!root && !careerSearch)return;
  const metadataPath=document.currentScript.dataset.metadataPath;
  const escapeRegExp=text=>text.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const matchesLocation=(location,value)=>value.toLowerCase()==='remote' ? location.toLowerCase().includes('remote') : location===value || location.split(';').some(part=>part.trim()===value);
  if(typeof module!=='undefined' && module.exports)module.exports={matchesLocation};
  fetch(metadataPath).then(response=>{if(!response.ok)throw Error('Careers metadata unavailable');return response.json();}).then(metadata=>{
    if(careerSearch){
      const input=careerSearch.querySelector('input[placeholder="Search"]');
      const dropdown=careerSearch.querySelector('.dropdown-button');
      const content=careerSearch.querySelector('.dropdown-content');
      const search=careerSearch.querySelector('a[aria-label^="Search SpaceX"]');
      let program='';
      const close=()=>{content.hidden=true;dropdown.setAttribute('aria-expanded','false');};
      const choices=()=>{
        content.replaceChildren();
        for(const value of [null,...metadata.programs].filter(value=>(value || '')!==program)){
          const button=document.createElement('button');button.type='button';button.className='dropdown-item';button.dataset.sx='dropdown';button.textContent=value || 'All Programs';
          button.addEventListener('click',()=>{program=value || '';dropdown.querySelector('span').textContent=program || 'All Programs';close();choices();dropdown.focus();});content.append(button);
        }
      };
      close();choices();dropdown.addEventListener('click',()=>{const open=content.hidden;content.hidden=!open;dropdown.setAttribute('aria-expanded',String(open));});
      document.addEventListener('click',event=>{if(!event.target.closest('[data-sx-host="dropdown"]'))close();});
      document.addEventListener('keydown',event=>{if(event.key==='Escape'){close();}});
      const destination=careerSearch.querySelector('a.career-link[href]');
      const submit=()=>{const target=new URL(destination.getAttribute('href'),location.href);if(input.value)target.searchParams.set('keyword',input.value);if(program)target.searchParams.set('programs',program);location.assign(target.href);};
      search.setAttribute('role','button');search.addEventListener('click',submit);search.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();submit();}});
      input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();submit();}});
    }
    if(!root)return;
    const keyword=root.querySelector('[data-careers-keyword]');
    const groups=[...root.querySelectorAll('[data-careers-group]')];
    const groupContainer=root.querySelector('[data-job-groups]');
    const rows=[...root.querySelectorAll('[data-careers-job]')].map(node=>({node,title:node.querySelector('.job-title-link').textContent,location:node.querySelector('.job-location').textContent,discipline:node.dataset.discipline,programs:[...node.querySelector('.job-programs').content.querySelectorAll('span')].map(e=>e.textContent)}));
    const fields=['programs','locations','disciplines'];
    const state={keyword:'',programs:new Set(),locations:new Set(),disciplines:new Set()};
    const readQuery=()=>{const params=new URLSearchParams(location.search);state.keyword=params.get('keyword') || '';keyword.value=state.keyword;fields.forEach(field=>{state[field]=new Set((params.get(field)||'').split('|').filter(Boolean));});};
    const highlight=(link,title,needle)=>{
      link.replaceChildren();if(!needle){link.textContent=title;return;}
      const regex=new RegExp(escapeRegExp(needle),'gi');let cursor=0;
      for(const match of title.matchAll(regex)){link.append(document.createTextNode(title.slice(cursor,match.index)));const span=document.createElement('span');span.className='highlighted-keyword';span.textContent=match[0];link.append(span);cursor=match.index+match[0].length;}
      link.append(document.createTextNode(title.slice(cursor)));
    };
    const render=()=>{
      const needle=state.keyword.trim().toLowerCase();let total=0;
      for(const row of rows){
        const visible=(!state.programs.size || row.programs.some(p=>state.programs.has(p))) && (!state.locations.size || [...state.locations].some(v=>matchesLocation(row.location,v))) && (!state.disciplines.size || state.disciplines.has(row.discipline)) && (!needle || row.title.toLowerCase().includes(needle) || row.location.toLowerCase().includes(needle));
        row.node.hidden=!visible;if(visible)total++;highlight(row.node.querySelector('.job-title-link'),row.title,state.keyword.trim());
      }
      const counts=new Map();
      for(const group of groups){const matching=rows.filter(row=>row.discipline===group.dataset.discipline && !row.node.hidden);counts.set(group,matching.length);group.hidden=!matching.length;const ul=group.querySelector('ul');rows.filter(row=>row.discipline===group.dataset.discipline).sort((a,b)=>a.title.localeCompare(b.title)).forEach(row=>ul.append(row.node));}
      groups.sort((a,b)=>counts.get(b)-counts.get(a) || a.dataset.discipline.localeCompare(b.dataset.discipline)).forEach(group=>groupContainer.append(group));
      root.querySelector('[data-careers-empty]').hidden=total!==0;
      for(const input of root.querySelectorAll('[data-careers-field]')){
        const set=state[input.dataset.careersField];
        if(input.hasAttribute('data-filter-any'))input.checked=set.size===0;
        else if(input.dataset.filterCategory){const children=metadata.disciplines[input.dataset.filterCategory].disciplines;const count=children.filter(v=>set.has(v)).length;input.checked=count===children.length;input.indeterminate=count>0 && count<children.length;}
        else input.checked=set.has(input.dataset.filterValue);
      }
      const active=(state.keyword.trim()?1:0)+fields.reduce((sum,key)=>sum+state[key].size,0);
      const open=root.querySelector('[data-careers-action="open"]');open.textContent='Show Filters'+(active ? ` (${active})` : '');
      root.dataset.visibleJobCount=String(total);
    };
    const writeQuery=()=>{const target=new URL(location.href);state.keyword ? target.searchParams.set('keyword',state.keyword) : target.searchParams.delete('keyword');fields.forEach(field=>{state[field].size ? target.searchParams.set(field,[...state[field]].join('|')) : target.searchParams.delete(field);});if(target.href!==location.href)history.pushState(null,'',target.href);render();};
    for(const input of root.querySelectorAll('[data-careers-field]'))input.addEventListener('change',()=>{
      const set=state[input.dataset.careersField];
      if(input.hasAttribute('data-filter-any'))set.clear();
      else if(input.dataset.filterCategory){const children=metadata.disciplines[input.dataset.filterCategory].disciplines;if(children.every(v=>set.has(v)))children.forEach(v=>set.delete(v));else children.forEach(v=>set.add(v));}
      else set.has(input.dataset.filterValue) ? set.delete(input.dataset.filterValue) : set.add(input.dataset.filterValue);
      writeQuery();
    });
    let debounce;keyword.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>{state.keyword=keyword.value;writeQuery();},300);});
    const overlay=root.querySelector('.mobile-filter-overlay');const opener=root.querySelector('[data-careers-action="open"]');let oldFocus;
    const close=()=>{overlay.hidden=true;opener.setAttribute('aria-expanded','false');oldFocus?.focus();};
    root.querySelectorAll('[data-careers-action]').forEach(control=>{
      const action=()=>{switch(control.dataset.careersAction){case'open':oldFocus=document.activeElement;overlay.hidden=false;opener.setAttribute('aria-expanded','true');overlay.querySelector('.close-button').focus();break;case'close':case'apply':close();break;case'clear':state.keyword='';keyword.value='';fields.forEach(key=>state[key].clear());writeQuery();break;}};
      control.addEventListener('click',action);if(control.tagName!=='BUTTON')control.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();action();}});
    });
    root.querySelectorAll('[data-filter-section]').forEach(trigger=>{const field=trigger.dataset.filterSection;const panel=root.querySelector('.'+field.replace(/s$/,'')+'-scrollbar');const change=()=>{panel.hidden=!panel.hidden;trigger.setAttribute('aria-expanded',String(!panel.hidden));trigger.querySelector('svg')?.classList.toggle('rotate-180',!panel.hidden);};trigger.addEventListener('click',change);trigger.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();change();}});});
    root.querySelectorAll('[data-mobile-filter-section]').forEach(trigger=>{const section=trigger.parentElement;const panels=[...section.children].filter(e=>e!==trigger);const change=()=>{const expanded=trigger.getAttribute('aria-expanded')!=='true';trigger.setAttribute('aria-expanded',String(expanded));panels.forEach(e=>{e.hidden=!expanded;});};trigger.addEventListener('click',change);trigger.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();change();}});});
    document.addEventListener('keydown',event=>{if(overlay.hidden)return;if(event.key==='Escape'){event.preventDefault();close();}else if(event.key==='Tab'){const focusable=[...overlay.querySelectorAll('button,input,[tabindex="0"]')].filter(e=>!e.disabled && e.getClientRects().length);if(!focusable.length)return;const first=focusable[0],last=focusable[focusable.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}});
    overlay.addEventListener('click',event=>{if(event.target===overlay)close();});
    window.addEventListener('popstate',()=>{readQuery();render();});readQuery();render();
  }).catch(error=>console.warn(error.message));
})();
