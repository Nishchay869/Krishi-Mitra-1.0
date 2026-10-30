(() => {
  const dialog = document.getElementById('spray-details');
  if (!dialog || !dialog.showModal) return;
  const panels = [...dialog.querySelectorAll('[data-spray-panel]')];
  const point = dialog.querySelector('#spray-chart-point');
  const reading = dialog.querySelector('#spray-chart-reading');
  let opener;
  function select(index) {
    const active = panels[index];
    if (!active) return;
    panels.forEach((p, i) => { p.hidden = i !== index; });
    dialog.querySelectorAll('[data-spray-slot]').forEach(button => {
      button.setAttribute('aria-pressed', String(Number(button.dataset.spraySlot) === index));
    });
    const temp = Number(active.dataset.temp), humidity = Number(active.dataset.humidity);
    const valid = Number.isFinite(temp) && Number.isFinite(humidity) &&
      active.dataset.temp !== '' && active.dataset.humidity !== '';
    point.toggleAttribute('hidden', !valid || temp < -10 || temp > 50 || humidity < 0 || humidity > 100);
    if (valid) {
      point.setAttribute('cx', String(55 + (temp + 10) * 5.5));
      point.setAttribute('cy', String(225 - humidity * 2));
    }
    reading.textContent = valid ? `${temp} °C · ${humidity}%` : '—';
  }
  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-spray-slot], [data-spray-open]');
    if (!trigger) return;
    select(Number(trigger.dataset.spraySlot || 0));
    if (!dialog.open) {
      opener = trigger;
      dialog.showModal();
      document.body.classList.add('spray-dialog-open');
    }
  });
  dialog.querySelectorAll('[data-spray-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('close', () => {
    document.body.classList.remove('spray-dialog-open');
    opener?.focus({preventScroll: true});
  });
  dialog.addEventListener('click', event => {
    const bounds = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
  });
})();
