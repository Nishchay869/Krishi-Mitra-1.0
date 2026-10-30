(() => {
  'use strict';
  const picker = document.getElementById('fertilizer-crop');
  picker?.addEventListener('change', () => picker.form.requestSubmit());
  document.querySelectorAll('[data-adjust]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.target);
      const value = Number(input.value);
      if (!Number.isFinite(value)) return;
      const next = Math.max(Number(input.min), Math.min(Number(input.max), value + Number(button.dataset.adjust)));
      input.value = String(Math.round(next * 1000) / 1000);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });
  document.querySelectorAll('[data-nutrient]').forEach(badge => {
    const input = document.getElementById(`id_${badge.dataset.nutrient}`);
    input?.addEventListener('input', () => { badge.textContent = input.value; });
  });
  const invalid = document.querySelector('.nutrient-editor input.is-invalid');
  if (invalid) invalid.closest('details').open = true;
  document.querySelectorAll('.nutrient-editor input').forEach(input => {
    input.addEventListener('invalid', () => { input.closest('details').open = true; });
  });
})();
(() => {
  const filters = document.querySelector('[data-product-filters]');
  if (!filters) return;
  filters.hidden = false;
  filters.querySelectorAll('[data-product-filter]').forEach(button => {
    button.addEventListener('click', () => {
      filters.querySelectorAll('button').forEach(item => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      document.querySelectorAll('[data-product-code]').forEach(card => {
        card.hidden = button.dataset.productFilter !== 'all' && card.dataset.productCode !== button.dataset.productFilter;
      });
    });
  });
})();
(() => {
  const input = document.querySelector('[data-shop-location]');
  if (!input) return;
  const links = document.querySelectorAll('[data-shop-search]');
  const makeQuery = (product = '') => `${product ? product + ' ' : ''}fertilizer shops near ${input.value.trim() || 'me'}`;
  const updateLinks = () => {
    links.forEach(link => {
      const url = new URL('https://www.google.com/maps/search/');
      url.searchParams.set('api', '1');
      url.searchParams.set('query', makeQuery(link.dataset.shopProduct));
      link.href = url.href;
    });
  };
  input.addEventListener('input', updateLinks);
  const button = document.querySelector('[data-shop-geolocate]');
  const status = document.querySelector('[data-shop-status]');
  if (!button || !navigator.geolocation || !window.isSecureContext) return;
  button.hidden = false;
  button.addEventListener('click', () => {
    button.disabled = true;
    status.textContent = status.dataset.locating;
    const originalPlace = input.value;
    navigator.geolocation.getCurrentPosition(async position => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 8000);
      try {
        const {latitude, longitude} = position.coords;
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
            Math.abs(latitude) > 90 || Math.abs(longitude) > 180) throw new Error('Invalid position');
        const url = new URL('https://api.bigdatacloud.net/data/reverse-geocode-client');
        url.searchParams.set('latitude', String(latitude));
        url.searchParams.set('longitude', String(longitude));
        const language = document.documentElement.lang.split('-')[0];
        url.searchParams.set('localityLanguage', /^[a-z]{2}$/.test(language) ? language : 'en');
        const response = await fetch(url.href, {signal: controller.signal, credentials: 'omit', cache: 'no-store'});
        if (!response.ok) throw new Error('Place lookup failed');
        const place = await response.json();
        if (typeof place.lookupSource === 'string' && /ip/i.test(place.lookupSource)) throw new Error('GPS address unavailable');
        if (![place.locality, place.city].some(value => typeof value === 'string' && value.trim())) {
          throw new Error('Local place name unavailable');
        }
        const seen = new Set();
        const parts = [place.locality, place.city, place.principalSubdivision, place.postcode, place.countryName]
          .filter(value => {
            if (typeof value !== 'string' || !value.trim()) return false;
            const key = value.trim().toLocaleLowerCase();
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
          }).map(value => value.trim());
        // A typed correction made during the lookup takes precedence.
        if (input.value === originalPlace) {
          input.value = parts.join(', ');
          updateLinks();
          status.textContent = status.dataset.found;
        } else {
          status.textContent = '';
        }
      } catch {
        status.textContent = status.dataset.error;
      } finally {
        clearTimeout(timer);
        button.disabled = false;
      }
    }, () => {
      status.textContent = status.dataset.error;
      button.disabled = false;
    }, {enableHighAccuracy:true, timeout:10000, maximumAge:60000});
  });
})();
