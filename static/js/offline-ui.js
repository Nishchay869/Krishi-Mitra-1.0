// Cached public reference content only. No account details or conversations are stored.
(async () => {
  const manifest = await (await fetch('/static/i18n/manifest.json')).json();
  let generation = 0;
  const select = document.getElementById('offline-language');
  for (const language of manifest.languages) {
    const option = document.createElement('option');
    option.value = language.code; option.textContent = language.label; select.appendChild(option);
  }
  const tools = [
    ['Ask Assistant', 'A question today. A clearer tomorrow. Ask about crops, pests, irrigation, and schemes.'],
    ['Crop Advisor', 'Find the crops that feel at home in your soil and local climate.'],
    ['Yield Estimate', 'Look ahead to harvest. Estimate yield for your crop, season, and state.'],
    ['Disease Check', 'Something on a leaf? Share a photo to explore the cause and next steps.'],
    ['Weather & Advisory', 'Make plans with a five-day forecast and practical irrigation advice.'],
    ['Market Prices', 'Stay in the know with daily mandi prices and recent price changes.'],
  ];
  let code = 'en';
  try { code = localStorage.getItem('krishi-language') || 'en'; } catch { /* storage unavailable */ }
  if (!manifest.languages.some(language => language.code === code)) code = 'en';
  async function render(language) {
    const current = ++generation;
    const messages = await (await fetch(`/static/i18n/${language}.json`)).json();
    if (current !== generation) return;
    const t = text => messages[text] || text;
    document.documentElement.lang = language;
    document.documentElement.dir = manifest.languages.find(item => item.code === language)?.dir || 'ltr';
    select.value = language;
    document.querySelectorAll('[data-offline-text]').forEach(el => { el.textContent = t(el.dataset.offlineText); });
    const host = document.getElementById('offline-tools');
    host.replaceChildren();
    for (const [title, description] of tools) {
      const column = document.createElement('div'); column.className = 'col-sm-6 col-lg-4';
      const card = document.createElement('article'); card.className = 'card h-100';
      const body = document.createElement('div'); body.className = 'card-body';
      const heading = document.createElement('h3'); heading.className = 'h5'; heading.textContent = t(title);
      const paragraph = document.createElement('p'); paragraph.className = 'small text-muted mb-0'; paragraph.textContent = t(description);
      body.append(heading, paragraph); card.append(body); column.append(card); host.append(column);
    }
    try { localStorage.setItem('krishi-language', language); } catch { /* storage unavailable */ }
  }
  select.addEventListener('change', () => { void render(select.value); });
  document.getElementById('retry').addEventListener('click', () => location.assign('/'));
  await render(code);
})().catch(() => { /* Plain HTML stays readable if storage/cache was cleared. */ });
