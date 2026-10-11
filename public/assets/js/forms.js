/* Native form UI only. Private submission services are not reproduced. */
for (const host of document.querySelectorAll('supplier-submit-page, lead-submit-page, research-submit-page')) {
  const root = host.shadowRoot || host;
  const form = root.querySelector('form');
  if (!form) continue;
  const controls = [...form.querySelectorAll('input, select, textarea')];
  const submit = form.querySelector('button[type="submit"]') || form.querySelector('button');
  const field = name => root.querySelector(`[data-field="${name}"]`);
  const hiddenParent = element => {
    let current = element?.parentElement;
    while (current && current !== form) {
      if (current.hasAttribute('data-conditional')) return current;
      if (current.hidden) { current.dataset.conditional = 'true'; return current; }
      current = current.parentElement;
    }
  };
  const reveal = (element, visible) => { const target = hiddenParent(element); if (target) target.hidden = !visible; };
  const synchronize = () => {
    for (const input of controls) {
      if (input.type === 'checkbox') {
        input.closest('mat-checkbox')?.classList.toggle('mat-checkbox-checked', input.checked);
        input.setAttribute('aria-checked', String(input.checked));
      }
      if (input.type === 'radio') input.closest('mat-radio-button')?.classList.toggle('mat-radio-checked', input.checked);
    }
    const selected = name => field(name)?.querySelector('input:checked')?.value;
    reveal(field('spacexEmail'), selected('spacexPoc') === 'true');
    reveal(field('isWomenOwned'), selected('isSmallBusiness') === 'true');
    const website = field('companyWebsite');
    if (website) website.disabled = !!field('needsWebsite')?.querySelector('input')?.checked;
    const available = controls.filter(input => !input.closest('[hidden]') && !input.disabled);
    if (submit) submit.disabled = !available.every(input => input.validity.valid);
  };
  for (const input of controls) {
    const container = input.closest('.epdk-form-field');
    if (container?.querySelector('.epdk-asterisk') && !['checkbox','radio'].includes(input.type)) input.required = true;
    if (/email/i.test(input.dataset.field || input.id)) input.type = 'email';
    input.addEventListener('input', synchronize);
    input.addEventListener('change', synchronize);
  }
  for (const group of form.querySelectorAll('mat-radio-group')) {
    if (group.closest('.epdk-form-field')?.querySelector('.epdk-asterisk')) group.querySelector('input').required = true;
  }
  for (const name of ['confirmedInfoChecked','itarChecked','confirmedInformationAccuracy']) {
    const input = field(name)?.querySelector('input'); if (input) input.required = true;
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    let status = form.querySelector('[data-service-status]');
    if (!status) { status = document.createElement('p'); status.dataset.serviceStatus = ''; status.setAttribute('role','status'); form.append(status); }
    status.textContent = 'Submission is unavailable in this offline reconstruction. No information has been sent.';
  });
  synchronize();
}
