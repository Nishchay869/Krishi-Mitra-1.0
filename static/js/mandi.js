(() => {
  const form = document.getElementById('mandi-filters');
  if (!form) return;
  const t = text => typeof window.gettext === 'function' ? window.gettext(text) : text;
  const status = document.getElementById('mandi-location-status');
  const dialog = document.getElementById('mandi-radius-dialog');
  document.getElementById('mandi-radius-open').addEventListener('click', () => {
    const current = document.getElementById('mandi-radius-value').value;
    dialog.querySelectorAll('[name=radius]').forEach(radio => { radio.checked = radio.value === current; });
    dialog.showModal();
  });
  document.getElementById('mandi-radius-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  document.getElementById('mandi-sort').addEventListener('change', event => {
    document.getElementById('mandi-sort-value').value = event.target.value;
    form.requestSubmit();
  });
  form.addEventListener('change', event => {
    if (event.target.name === 'state') {
      form.elements.district.disabled = true;
      form.elements.market.disabled = true;
    } else if (event.target.name === 'district') {
      form.elements.market.disabled = true;
    }
    form.requestSubmit();
  });
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  document.querySelectorAll('.mandi-favourite-form').forEach(starForm => {
    starForm.addEventListener('submit', async event => {
      event.preventDefault();
      const button = starForm.querySelector('button');
      button.disabled = true;
      try {
        const response = await fetch(starForm.getAttribute('action'), {method:'POST', body:new FormData(starForm), headers:{Accept:'application/json'}, credentials:'same-origin'});
        if (!response.ok || response.redirected) throw new Error();
        const result = await response.json();
        document.querySelectorAll('.mandi-favourite-form').forEach(other => {
          if (other.dataset.marketId !== starForm.dataset.marketId) return;
          other.elements.action.value = result.favourite ? 'remove' : 'add';
          other.querySelector('button').setAttribute('aria-pressed', String(result.favourite));
          other.querySelector('i').className = `bi ${result.favourite ? 'bi-star-fill' : 'bi-star'}`;
        });
        status.textContent = result.favourite ? t('Market saved to favourites.') : t('Market removed from favourites.');
        if (!result.favourite && new URL(location.href).searchParams.get('favourites') === '1') location.reload();
      } catch (_) {
        status.textContent = t('Could not save favourites. Please try again.');
      } finally { button.disabled = false; }
    });
  });
  const locationButton = document.getElementById('mandi-use-location');
  locationButton.addEventListener('click', () => {
    if (!navigator.geolocation) {
      status.textContent = t('Location is unavailable. Please check your browser permissions.');
      return;
    }
    locationButton.disabled = true;
    status.textContent = t('Finding your location…');
    navigator.geolocation.getCurrentPosition(async position => {
      const {latitude, longitude} = position.coords;
      let label = '';
      try {
        // BigDataCloud's client-only endpoint receives only this device's location.
        const url = new URL('https://api.bigdatacloud.net/data/reverse-geocode-client');
        url.search = new URLSearchParams({latitude, longitude, localityLanguage:document.documentElement.lang || 'en'});
        const response = await fetch(url, {signal:AbortSignal.timeout(8000)});
        if (response.ok) {
          const place = await response.json();
          if (!place.isBasedOnIpAddress && !/ip/i.test(place.lookupSource || '')) label = [...new Set([place.locality, place.city, place.principalSubdivision].filter(Boolean))].join(', ');
        }
      } catch (_) { /* Distances still use the device point if its name cannot be resolved. */ }
      try {
        const response = await fetch(locationButton.dataset.url, {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json','X-CSRFToken':csrf()}, body:JSON.stringify({latitude,longitude,label:label || t('Your current location')})});
        if (!response.ok || response.redirected) throw new Error();
        const url = new URL(location.href);
        url.searchParams.set('district',''); url.searchParams.set('market','');
        location.assign(url.href);
      } catch (_) {
        status.textContent = t('Location could not be saved. Please try again.');
        locationButton.disabled = false;
      }
    }, () => {
      status.textContent = t('Location is unavailable. Please check your browser permissions.');
      locationButton.disabled = false;
    }, {enableHighAccuracy:true, timeout:12000, maximumAge:60000});
  });
})();

/* data.gov.in refuses some servers (e.g. hosting outside India) but allows browsers.
   When the page asks for it, fetch the mandi records here, hand them to the server
   (validated + kept for this farmer only), then reload to show them normally. */
(() => {
  const box = document.getElementById('mandi-browser-fetch');
  const cfgEl = document.getElementById('mandi-browser-fetch-config');
  if (!box || !cfgEl) return;
  const cfg = JSON.parse(cfgEl.textContent);
  const csrf = (document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1] || '';
  const reloadSeeded = () => {
    const url = new URL(window.location.href);
    url.searchParams.set('seeded', '1');
    window.location.replace(url.toString());
  };

  (async () => {
    const records = [];
    let offset = 0, total = Infinity;
    try {
      for (let page = 0; page < 5 && offset < total; page++) {
        const url = new URL(cfg.endpoint);
        url.search = new URLSearchParams({
          'api-key': cfg.api_key, format: 'json', limit: '200', offset: String(offset),
          'filters[state]': cfg.state, 'filters[commodity]': cfg.crop,
        }).toString();
        const resp = await fetch(url, { cache: 'no-store' });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const batch = Array.isArray(data.records) ? data.records : [];
        total = Number(data.total) || 0;
        records.push(...batch);
        offset += batch.length;
        if (!batch.length) break;
      }
      await fetch(box.dataset.seedUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(csrf) },
        body: JSON.stringify({ state: cfg.state, crop: cfg.crop, records, truncated: offset < total }),
      });
    } catch (err) {
      console.warn('Mandi prices could not be fetched in the browser:', err);
    }
    reloadSeeded(); // shows the prices, or the "unavailable" message if this failed too
  })();
})();
