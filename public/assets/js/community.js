/* Captured Mid-South dialog UI; private submission services remain unavailable. */
let communityDialog = null;
let communityReturn = null;
let communityInert = [];
let communityOverflow = '';
// Rules are bounded to the two captured public community forms.
const communityRequiredMessages = {
  'Organization name':'Enter an organization name.', 'Contact name':'Enter a contact name.',
  'Please specify':'Please specify the organization type.', 'First Name':'Enter a first name.',
  'Last Name':'Enter a last name.', 'Feedback or Suggestions':'Enter feedback or suggestions.'
};
const communityChoiceMessages = {
  'Which sites are you interested in':'Select at least one site.', 'Skillsets':'Select at least one skillset.',
  'Organization type':'Select an organization type.', 'City':'Select a city.', 'State':'Select a state.'
};
const communityClearError = field => {
  field.querySelector('[data-community-error]')?.remove();
  field.querySelectorAll('.is-invalid').forEach(e=>e.classList.remove('is-invalid'));
  field.querySelectorAll('[aria-invalid]').forEach(e=>e.removeAttribute('aria-invalid'));
};
const communityError = (control, message) => {
  const field = control.closest('label');
  control.classList.add('is-invalid'); control.setAttribute('aria-invalid','true');
  const error = document.createElement('span'); error.className = 'partner-form__hint'; error.dataset.communityError = ''; error.textContent = message; field.append(error);
};
const validateCommunity = (form, kind) => {
  form.querySelectorAll('label').forEach(communityClearError);
  let valid = true;
  for (const input of form.querySelectorAll('input,textarea')) {
    if (input.disabled) continue;
    const label = input.getAttribute('aria-label'); const value = input.value.trim(); let message = '';
    if (communityRequiredMessages[label] && !value) message = communityRequiredMessages[label];
    if (label === 'Email') message = !value ? (kind==='partner'?'Enter an email.':'Enter an email address.') : /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,})+$/.test(value) ? '' : (kind==='partner'?'Enter a valid email.':'Enter a valid email address.');
    if (label === 'Phone' && value) { let digits = value.replace(/\D/g,''); if (digits.length===11 && digits.startsWith('1')) digits=digits.slice(1); if (digits.length!==10) message='Enter a 10-digit phone number.'; }
    if (label === 'People per year' && (!value || !(Number(value)>0))) message='Enter how many people you can place per year.';
    if (label === 'Zip Code') message = !value ? 'Enter a zip code.' : /^\d{5}(-\d{4})?$/.test(value) ? '' : 'Enter a 5-digit zip code.';
    if (message) { communityError(input,message); valid=false; }
  }
  for (const group of form.querySelectorAll('[data-required-choice="true"]')) {
    if (group.querySelector('[role="option"][aria-selected="true"]')) continue;
    const trigger=group.querySelector('button'); communityError(trigger,communityChoiceMessages[trigger.getAttribute('aria-label')]); valid=false;
  }
  return valid;
};

const closeCommunity = () => {
  if (!communityDialog) return;
  communityDialog.remove(); communityDialog = null;
  communityInert.forEach(([element,previous]) => { element.inert = previous; }); communityInert = [];
  document.body.style.overflow = communityOverflow;
  communityReturn?.focus();
};
const showCommunity = trigger => {
  const source = document.querySelector(`template[data-community-template="${trigger.dataset.communityOpen}"]`);
  if (!source) return;
  closeCommunity(); communityReturn = trigger;
  communityDialog = source.content.firstElementChild.cloneNode(true);
  const parent = trigger.closest('.page--memphis') || document.body;
  parent.append(communityDialog);
  let child = communityDialog;
  while (child.parentElement) {
    for (const sibling of child.parentElement.children) if (sibling !== child && !['SCRIPT','STYLE','TEMPLATE'].includes(sibling.tagName)) {
      communityInert.push([sibling,sibling.inert]); sibling.inert = true;
    }
    child = child.parentElement; if (child === document.body) break;
  }
  communityOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden';
  communityDialog.querySelector('button')?.focus();
  communityDialog.querySelector('form').addEventListener('submit', event => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!validateCommunity(form,communityDialog.dataset.communityDialog)) return;
    let status = form.querySelector('[data-service-status]');
    if (!status) { status = document.createElement('p'); status.dataset.serviceStatus = ''; status.setAttribute('role','status'); form.append(status); }
    status.textContent = 'Submission is unavailable in this reconstruction. No information has been sent.';
  });
};
document.addEventListener('click', event => {
  const open = event.target.closest('[data-community-open]');
  if (open) { event.preventDefault(); showCommunity(open); return; }
  if (!communityDialog) return;
  if (event.target === communityDialog || event.target.closest('.partner-dialog__close')) { closeCommunity(); return; }
  const group = event.target.closest('[data-community-choice]');
  if (!group || !communityDialog.contains(group)) return;
  const trigger = group.querySelector('.partner-ms__trigger'); const menu = group.querySelector('[role="listbox"]');
  const option = event.target.closest('[role="option"]');
  if (option) {
    const selected = group.dataset.multiple === 'true' ? option.getAttribute('aria-selected') !== 'true' : true;
    if (group.dataset.multiple !== 'true') menu.querySelectorAll('[role="option"]').forEach(item => { item.setAttribute('aria-selected','false'); item.classList.remove('is-on'); });
    option.setAttribute('aria-selected',String(selected)); option.classList.toggle('is-on',selected);
    const values = [...menu.querySelectorAll('[aria-selected="true"]')].map(item=>item.textContent.trim());
    trigger.querySelector('span').textContent = values.length ? values.join(', ') : group.dataset.placeholder;
    communityClearError(trigger.closest('label'));
    if (trigger.getAttribute('aria-label') === 'Organization type') {
      const extra = communityDialog.querySelector('[data-other-organization]');
      extra.hidden = !values.includes('Other'); extra.querySelector('input').disabled = extra.hidden; if (extra.hidden) extra.querySelector('input').value = '';
    }
    if (group.dataset.multiple !== 'true') { menu.hidden = true; group.classList.remove('is-open'); trigger.setAttribute('aria-expanded','false'); trigger.focus(); }
  } else if (event.target.closest('.partner-ms__trigger')) {
    menu.hidden = !menu.hidden; group.classList.toggle('is-open',!menu.hidden); trigger.setAttribute('aria-expanded',String(!menu.hidden));
  }
});
document.addEventListener('keydown', event => {
  if (!communityDialog) return;
  if (event.key === 'Escape') { event.preventDefault(); closeCommunity(); return; }
  if (event.key !== 'Tab') return;
  const choices = [...communityDialog.querySelectorAll('button,input,textarea,select,a[href]')].filter(e=>!e.disabled && !e.closest('[hidden]') && e.getClientRects().length);
  const first = choices[0], last = choices.at(-1);
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
});

document.addEventListener('input', event => {
  if (!communityDialog || !communityDialog.contains(event.target)) return;
  const input = event.target; const label = input.getAttribute('aria-label');
  if (label === 'Phone') {
    let digits = input.value.replace(/\D/g,''); if (digits.length===11 && digits.startsWith('1')) digits=digits.slice(1); digits=digits.slice(0,10);
    input.value = !digits ? '' : digits.length<4 ? '('+digits : digits.length<7 ? '('+digits.slice(0,3)+') '+digits.slice(3) : '('+digits.slice(0,3)+') '+digits.slice(3,6)+'-'+digits.slice(6);
  }
  if (label === 'Zip Code') { const digits=input.value.replace(/\D/g,'').slice(0,9); input.value=digits.length<=5 ? digits : digits.slice(0,5)+'-'+digits.slice(5); }
  if (input.closest('label')) communityClearError(input.closest('label'));
});
