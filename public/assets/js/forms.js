/* Delivered public numeric directive semantics; no private service implementation. */
const publicNumericText = (value, options = {}) => {
  if (!value) return false;
  const {allowCommas,allowDecimal,allowNegative,allowCurrency,liveTypingMode} = options;
  let commas=0,decimals=0,negatives=0,currency=0,digits=false;
  for (const char of value) {
    if (/\d/.test(char)) digits=true;
    else if (char===',') commas++;
    else if (char==='.') decimals++;
    else if (char==='-') negatives++;
    else if (char==='$') currency++;
    else return false;
  }
  if (!digits) return !!liveTypingMode && ['.', '-', '$', '-.', '$.', '-$', '-$.'].includes(value) && (!value.includes('.') || allowDecimal) && (!value.includes('-') || allowNegative) && (!value.includes('$') || allowCurrency);
  if (commas && !allowCommas || decimals && !allowDecimal || negatives && !allowNegative || currency && !allowCurrency || decimals>1 || negatives>1 || currency>1) return false;
  if (negatives && !value.startsWith('-') || currency && !value.startsWith('$') && !value.startsWith('-$') || /\..*,/.test(value) || /,,/.test(value)) return false;
  return liveTypingMode || !value.endsWith(',');
};
/* Native form UI only. Private submission services are not reproduced. */
for (const host of document.querySelectorAll('supplier-submit-page, lead-submit-page, research-submit-page')) {
  const root = host.shadowRoot || host;
  const form = root.querySelector('form');
  if (!form) continue;
  const controls = () => [...form.querySelectorAll('input, select, textarea')];
  let repeatIdentity = 0;
  const identifyRow = row => {
    for (const input of row.querySelectorAll('input,select')) {
      const old = input.id; input.id = 'native-code-' + (++repeatIdentity);
      if (old) row.querySelectorAll('label').forEach(label => { if (label.htmlFor === old) label.htmlFor = input.id; });
    }
  };
  form.querySelectorAll('[data-repeat-row]').forEach(identifyRow);
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
    for (const input of controls()) {
      if (input.type === 'checkbox') {
        input.closest('mat-checkbox')?.classList.toggle('mat-checkbox-checked', input.checked);
        input.setAttribute('aria-checked', String(input.checked));
      }
      if (input.type === 'radio') input.closest('mat-radio-button')?.classList.toggle('mat-radio-checked', input.checked);
    }
    const selected = name => field(name)?.querySelector('input:checked')?.value;
    reveal(field('spacexEmail'), selected('spacexPoc') === 'true');
    reveal(field('isWomenOwned'), selected('isSmallBusiness') === 'true');
    const naics = selected('naicsCodes');
    form.querySelectorAll('[data-naics-condition]').forEach(block => { block.hidden = block.dataset.naicsCondition === 'yes' ? naics !== 'true' : naics !== 'false'; });
    const naicsList = form.querySelector('[data-repeat-list="naics"]');
    if (naicsList && naics === 'false') naicsList.replaceChildren();
    if (naicsList && naics === 'true' && !naicsList.children.length) {
      const row = form.querySelector('[data-repeat-template="naics"]').content.firstElementChild.cloneNode(true);
      identifyRow(row); naicsList.append(row);
    }
    const construction = selected('providesConstructionServices');
    form.querySelectorAll('[data-csi-condition]').forEach(block => { block.hidden = !construction || construction === 'No'; });
    // Hidden required fields cannot block a visible form branch.
    for (const input of controls()) input.disabled = !!input.closest('[hidden]');
    const website = field('companyWebsite');
    if (website) website.disabled = !!field('needsWebsite')?.querySelector('input')?.checked;
    for (const input of form.querySelectorAll('[data-code-field="naics"]')) input.required = true;
    for (const row of form.querySelectorAll('[data-repeat-row="csi"]')) {
      const select = row.querySelector('select'); select.required = true;
      const sub = row.querySelector('input'); sub.pattern = '[0-9]{6}';
    }
    const available = controls().filter(input => !input.closest('[hidden]') && !input.disabled);
    const revenue = field('approxRevenue');
    if (revenue) revenue.setCustomValidity(!revenue.value || publicNumericText(revenue.value, {allowCommas:true,allowDecimal:true,allowCurrency:true}) ? '' : 'Revenue must be a valid number.');
    if (host.tagName === 'SUPPLIER-SUBMIT-PAGE') {
      for (const name of ['spacexEmail','pocEmail']) {
        const input = field(name);
        if (input) input.setCustomValidity(!input.value || /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(input.value) ? '' : 'Enter a valid email address.');
      }
    }
    if (host.tagName === 'SUPPLIER-SUBMIT-PAGE') {
      for (const name of ['companyLegalName','companyAddress','country','companyWebsite','approxRevenue','spacexEmail','specializationDescription','pocJobTitle','pocGivenName','pocFamilyName','pocEmail','pocPhone']) {
        const input=field(name);const indicator=input?.closest('.epdk-form-field')?.querySelector('epdk-asterisk');
        if (indicator) indicator.style.display=(name==='approxRevenue' ? input.validity.valid : !!input.value && input.validity.valid) ? 'none' : '';
      }
      for (const group of form.querySelectorAll('mat-radio-group[data-field]')) {
        const indicator=group.closest('.epdk-form-field')?.querySelector('epdk-asterisk');
        if (indicator) indicator.style.display=group.querySelector('input:checked') ? 'none' : '';
      }
    }
    if (submit) submit.disabled = !available.every(input => input.validity.valid);
  };
  for (const input of controls()) {
    if (input.tagName === 'TEXTAREA' && !input.value.trim()) input.value = '';
    const container = input.closest('.epdk-form-field');
    if (host.tagName === 'SUPPLIER-SUBMIT-PAGE') {
      input.required = ['companyLegalName','companyAddress','country','companyWebsite','spacexEmail','specializationDescription','pocJobTitle','pocGivenName','pocFamilyName','pocEmail','pocPhone'].includes(input.dataset.field);
    } else if (container?.querySelector('.epdk-asterisk') && !['checkbox','radio'].includes(input.type)) input.required = true;
    if (/email/i.test(input.dataset.field || input.id)) input.type = 'email';

  }
  for (const group of form.querySelectorAll('mat-radio-group')) {
    const required = host.tagName === 'SUPPLIER-SUBMIT-PAGE'
      ? ['spacexPoc','isSmallBusiness','isHbcu','isIsoCert','isAsCert','naicsCodes','providesConstructionServices'].includes(group.dataset.field)
      : !!group.closest('.epdk-form-field')?.querySelector('.epdk-asterisk');
    if (required) group.querySelector('input').required = true;
  }
  for (const name of ['confirmedInfoChecked','itarChecked','confirmedInformationAccuracy']) {
    const input = field(name)?.querySelector('input'); if (input) input.required = true;
  }
  const numericFields = [...form.querySelectorAll('[constraintonumber]')];
  const lastGoodNumber = new WeakMap();
  numericFields.forEach(input => {
    lastGoodNumber.set(input,input.value);
    input.addEventListener('beforeinput',()=>lastGoodNumber.set(input,input.value));
    input.addEventListener('input',()=>{
      const options={liveTypingMode:true,allowDecimal:input.getAttribute('allowdecimal')==='true',allowCommas:input.getAttribute('allowcommas')==='true',allowCurrency:input.getAttribute('allowcurrency')==='true'};
      if (input.value && !publicNumericText(input.value,options)) input.value=lastGoodNumber.get(input) || '';
      else lastGoodNumber.set(input,input.value);
    });
  });
  form.addEventListener('input', event => {
    if (event.target.matches('[data-code-field="naics"]')) event.target.value = event.target.value.replace(/[^0-9]/g,'');
    synchronize();
  });
  form.addEventListener('change', synchronize);
  form.addEventListener('click', event => {
    const add = event.target.closest('[data-add-code]');
    const remove = event.target.closest('[data-remove-code]');
    if (add) {
      event.preventDefault();
      const kind = add.dataset.addCode;
      const row = form.querySelector(`[data-repeat-template="${kind}"]`).content.firstElementChild.cloneNode(true);
      identifyRow(row); if (kind === 'csi') row.querySelector('select').selectedIndex = -1; form.querySelector(`[data-repeat-list="${kind}"]`).append(row); row.querySelector('input,select')?.focus();
    } else if (remove) {
      event.preventDefault(); const row = remove.closest('[data-repeat-row]'); const list = row.parentElement;
      if (row.dataset.repeatRow === 'naics' && list.children.length === 1) return;
      row.remove(); list.querySelector('input,select')?.focus();
    } else return;
    synchronize();
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    let status = form.querySelector('[data-service-status]');
    if (!status) { status = document.createElement('p'); status.dataset.serviceStatus = ''; status.setAttribute('role','status'); form.append(status); }
    status.textContent = 'Submission is unavailable in this offline reconstruction. No information has been sent.';
  });
  synchronize();
}

// Newsletter validation is local; the original private subscription API is unavailable.
const initializeNewsletters = () => {
const forms = [...document.querySelectorAll('email-signup')].map(host => (host.shadowRoot || host).querySelector('[data-newsletter-form]')).concat([...document.querySelectorAll('form[data-newsletter-form]')]);
for (const form of forms) {
  const root = form?.parentElement;
  if (!form) continue;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    let status = root.querySelector('[data-service-status]');
    if (!status) { status = document.createElement('p'); status.dataset.serviceStatus = ''; status.setAttribute('role', 'status'); form.after(status); }
    status.textContent = 'Subscription is unavailable in this reconstruction. No information has been sent.';
  });
}
};
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializeNewsletters, { once: true });
else initializeNewsletters();
