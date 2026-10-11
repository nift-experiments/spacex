/* Maintained complete launch rows; filtering and pagination never call the CMS. */
const completed = document.querySelector('[data-completed-launches]');
if (completed) {
  const rows = [...completed.querySelectorAll('tr[data-route]')];
  const fields = ['missionType', 'vehicle', 'launchSite', 'returnSite', 'year'];
  const filters = [...completed.closest('table').querySelectorAll('.filter')];
  const selected = fields.map(() => new Set());
  const paginator = document.querySelector('paginator');
  const previous = paginator.querySelectorAll('.paginator-button')[0];
  const next = paginator.querySelectorAll('.paginator-button')[1];
  const sizeButton = paginator.querySelector('.dropdown-button');
  const options = paginator.querySelector('.dropdown-content');
  const search = document.querySelector('input[placeholder="Search mission name"]');
  let page = 0, size = 10;
  const render = () => {
    const needle = (search?.value || '').toLowerCase();
    const matching = rows.filter(row => row.dataset.title.toLowerCase().includes(needle) && fields.every((field,index) => !selected[index].size || selected[index].has(row.dataset[field]) || (field === 'missionType' && selected[index].has('Direct to Cell') && row.dataset.directToCell === 'true')));
    page = Math.min(page, Math.max(0, Math.ceil(matching.length / size) - 1));
    rows.forEach(row => {row.hidden = true;});
    matching.slice(page * size, (page + 1) * size).forEach(row => {row.hidden = false;});
    paginator.querySelector('.page-text').textContent = `${matching.length ? page * size + 1 : 0}-${Math.min((page+1)*size,matching.length)} OF ${matching.length}`;
    previous.disabled = page === 0; next.disabled = (page + 1) * size >= matching.length;
    filters.forEach((filter,index) => {
      filter.querySelector('.clear').classList.toggle('show', selected[index].size > 0);
      filter.querySelectorAll('.filter-item').forEach(item => {const chosen = selected[index].has(item.textContent.trim()); item.classList.toggle('selected', chosen); item.setAttribute('aria-pressed', String(chosen));});
    });
  };
  const dismiss = () => {
    filters.forEach(filter => {filter.querySelector('.filter-content').hidden=true; filter.querySelector('.filter-button').setAttribute('aria-expanded','false');});
    options.classList.remove('open'); options.hidden = true; sizeButton.setAttribute('aria-expanded','false');
  };
  filters.forEach((filter,index) => {
    const trigger = filter.querySelector('.filter-button');
    const panel = filter.querySelector('.filter-content');panel.hidden=true;trigger.setAttribute('aria-expanded','false');
    trigger.addEventListener('click', event => {
      if (event.target.closest('.clear')) {selected[index].clear();page=0;render();return;}
      const open=panel.hidden;dismiss();panel.hidden=!open;panel.classList.toggle('open',open);trigger.setAttribute('aria-expanded',String(open));
    });
    filter.querySelectorAll('.filter-item').forEach(item => item.addEventListener('click', () => {
      const value = item.textContent.trim();selected[index].has(value) ? selected[index].delete(value) : selected[index].add(value);page=0;render();
    }));
  });
  previous.setAttribute('aria-label','Previous launches'); next.setAttribute('aria-label','Next launches');
  previous.addEventListener('click',()=>{page--;render();});next.addEventListener('click',()=>{page++;render();});
  search?.setAttribute('aria-label','Search mission name');search?.addEventListener('input',()=>{page=0;render();});
  sizeButton.setAttribute('aria-label','Launches per page');sizeButton.setAttribute('aria-expanded','false');options.hidden=true;
  const updateSizes=()=>{
    options.replaceChildren();
    for (const value of [10,25,50].filter(value=>value!==size)) {
      const option=document.createElement('span');option.textContent=String(value);option.dataset.sx='paginator';option.setAttribute('role','button');option.tabIndex=0;
      const choose=()=>{size=value;page=0;sizeButton.querySelector('span').textContent=String(size);dismiss();updateSizes();render();sizeButton.focus();};
      option.addEventListener('click',choose);option.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose();}});options.append(option);
    }
  };
  sizeButton.addEventListener('click',()=>{const open=options.hidden;dismiss();options.hidden=!open;options.classList.toggle('open',open);sizeButton.setAttribute('aria-expanded',String(open));});
  document.addEventListener('click',event=>{if(!event.target.closest('.filter')&&!event.target.closest('paginator .dropdown'))dismiss();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape')dismiss();});
  rows.forEach(row=>{row.addEventListener('click',()=>location.assign(row.dataset.route));row.addEventListener('keydown',event=>{if(event.key==='Enter')location.assign(row.dataset.route);});});
  updateSizes();render();
}

// Ongoing and upcoming rows preserve their public mission destination.
for (const row of document.querySelectorAll('tr[data-active-launch]')) {
  row.addEventListener('click', () => location.assign(row.dataset.route));
  row.addEventListener('keydown', event => {
    if (event.key === 'Enter') location.assign(row.dataset.route);
  });
}
