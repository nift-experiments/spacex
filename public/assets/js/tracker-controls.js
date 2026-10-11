/* Native vehicle selection bridge for the delivered public vanilla renderer. */
const trackerHost = document.querySelector('vehicle-tracker');
if (trackerHost) {
  const container = trackerHost.querySelector('#vehicles');
  const displayName = id => {
    const crew = /^crew(\d+)$/.exec(id);
    const cargo = /^crs(\d+)$/.exec(id);
    if (crew) return 'crew-' + crew[1];
    if (cargo) return 'crs-' + cargo[1];
    return id === 'ship41' ? 'Flight 14' : id === 'ship42' ? 'Flight 15' : id;
  };
  const select = id => {
    const vehicle = window.vehicles?.[id];
    if (!vehicle) return;
    window.isRotated = false;
    window.setFeatured?.(id);
    window.rotateToLocation?.(vehicle.position.x, vehicle.position.y, vehicle.position.z);
    window.updateTelemetryFromVehicle?.(id);
    update();
  };
  const update = () => {
    const ids = Object.keys(window.currentVehicles || {});
    for (const button of [...container.querySelectorAll('[data-vehicle-id]')]) {
      if (!ids.includes(button.dataset.vehicleId)) button.parentElement.remove();
    }
    for (const id of ids) {
      let button = [...container.querySelectorAll('[data-vehicle-id]')].find(item => item.dataset.vehicleId === id);
      if (!button) {
        const owner = document.createElement('div');
        owner.className = 'sx-button'; owner.dataset.sxHost = 'spx-button';
        button = document.createElement('a');
        button.className = 'spx-button thin'; button.dataset.sx = 'spx-button'; button.dataset.vehicleId = id;
        button.tabIndex = 0; button.setAttribute('role', 'button');
        button.style.paddingLeft = '12px'; button.style.paddingRight = '12px'; button.style.marginTop = '0';
        const text = document.createElement('div'); text.className = 'text'; text.dataset.sx = 'spx-button'; text.textContent = displayName(id);
        button.append(text); owner.append(button); container.append(owner);
        button.addEventListener('click', () => select(id));
        button.addEventListener('keydown', event => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); select(id);}});
      }
      const selected = id === window.featuredVehicle;
      button.classList.toggle('selected', selected); button.setAttribute('aria-pressed', String(selected));
    }
  };
  window.onTrackerUpdate = update;
  update();
  setInterval(update, 10000);
}
