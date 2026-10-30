(() => {
  const form = document.getElementById('disease-form');
  if (!form) return;

  const input    = form.querySelector('input[type=file]');
  const preview  = document.getElementById('preview');
  const button   = document.getElementById('analyze-leaf');
  const resultEl = document.getElementById('result-container');
  const origLabel = button.innerHTML;
  let objectUrl  = '';

  /* ── Image preview ── */
  input?.addEventListener('change', () => {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    const file = input.files[0];
    if (!file) { preview.removeAttribute('src'); preview.classList.add('d-none'); return; }
    objectUrl = URL.createObjectURL(file);
    preview.src = objectUrl;
    preview.classList.remove('d-none');
  });

  /* ── AJAX submit ── */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validate file chosen
    if (!input.files[0]) {
      showError(t('Please choose a leaf photo first.'));
      return;
    }

    setLoading(true);
    clearResult();

    const data = new FormData(form);

    try {
      const res = await fetch(form.dataset.apiUrl || '/disease/api/', {
        method: 'POST',
        body: data,
        headers: { 'X-CSRFToken': getCsrf() },
      });

      const json = await res.json();

      if (!res.ok || json.error) {
        showError(json.error || t('Analysis failed. Please try again.'));
        return;
      }

      renderResult(json);
      document.getElementById('assessment-result')?.focus();

    } catch (err) {
      if (err.name === 'TypeError') {
        showError(t('Could not reach the server. Please check your connection.'));
      } else {
        showError(t('An unexpected error occurred. Please try again.'));
      }
    } finally {
      setLoading(false);
    }
  });

  /* ── Helpers ── */
  function t(s) { return typeof gettext === 'function' ? gettext(s) : s; }

  function getCsrf() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }

  function setLoading(on) {
    button.disabled = on;
    button.innerHTML = on
      ? `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>${t('Analyzing with Gemini…')}`
      : origLabel;
    if (on) showLoader();
  }

  function clearResult() {
    if (resultEl) resultEl.innerHTML = '';
  }

  function showLoader() {
    if (!resultEl) return;
    resultEl.innerHTML = `
      <div class="assessment-loading" role="status" aria-live="polite">
        <div class="assessment-loading-spinner">
          <span class="spinner-border" style="width:2.5rem;height:2.5rem;color:#6a9a4a" role="status"></span>
        </div>
        <p class="assessment-loading-text">${t('Gemini is analyzing your leaf photo…')}</p>
        <p class="assessment-loading-sub">${t('This usually takes 10–30 seconds.')}</p>
      </div>`;
  }

  function showError(msg) {
    if (!resultEl) return;
    resultEl.innerHTML = `
      <div class="alert alert-warning" role="alert">
        <strong>${t('The photo could not be analyzed.')}</strong>
        <p class="mb-0 mt-2">${esc(msg)}</p>
      </div>`;
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function li(items) {
    return items.map(i => `<li>${esc(i)}</li>`).join('');
  }

  function olli(items) {
    return items.map(i => `<li>${esc(i)}</li>`).join('');
  }

  function statusLabel(status) {
    const map = {
      likely_disease: t('Possible issue detected'),
      healthy: t('No obvious disease'),
      not_leaf: t('Leaf photo needed'),
      uncertain: t('Needs confirmation'),
    };
    return map[status] || t('Needs confirmation');
  }

  function diseaseTypeBadge(type) {
    if (!type || type === 'unknown') return '';
    const map = {
      fungal:        { icon: 'bi-circle-fill', label: t('Fungal Disease'),         cls: 'disease-type-fungal'        },
      bacterial:     { icon: 'bi-circle-fill', label: t('Bacterial Disease'),      cls: 'disease-type-bacterial'     },
      viral:         { icon: 'bi-circle-fill', label: t('Viral Disease'),          cls: 'disease-type-viral'         },
      pest:          { icon: 'bi-bug-fill',    label: t('Pest / Insect Damage'),   cls: 'disease-type-pest'          },
      nutritional:   { icon: 'bi-droplet-fill',label: t('Nutritional Deficiency'), cls: 'disease-type-nutritional'   },
      environmental: { icon: 'bi-thermometer-half', label: t('Environmental Stress'), cls: 'disease-type-environmental' },
    };
    const d = map[type];
    if (!d) return '';
    return `<div class="disease-type-badge ${d.cls}"><i class="bi ${d.icon}" aria-hidden="true"></i> ${d.label}</div>`;
  }

  function section(num, title, listType, items) {
    if (!items || !items.length) return '';
    const tag = listType === 'ol' ? 'ol' : 'ul';
    return `
      <section class="assessment-section">
        <span class="assessment-number">${num}</span>
        <div>
          <h3>${title}</h3>
          <${tag}>${listType === 'ol' ? olli(items) : li(items)}</${tag}>
        </div>
      </section>`;
  }

  function renderResult(r) {
    if (!resultEl) return;

    const certaintyLabel = { high: t('High'), medium: t('Medium'), low: t('Low') }[r.certainty] || t('Low');

    /* Chemical cards */
    let chemHtml = '';
    if (r.chemical_options && r.chemical_options.length) {
      chemHtml = r.chemical_options.map(opt => `
        <div class="assessment-chemical">
          <div class="chemical-header">
            <strong>${esc(opt.active_ingredient)}</strong>
            ${opt.chemical_group ? `<span class="chemical-group">${esc(opt.chemical_group)}</span>` : ''}
          </div>
          <p class="chemical-purpose">${esc(opt.purpose || '')}</p>
          ${opt.application_method ? `<div class="chemical-detail"><i class="bi bi-spray" aria-hidden="true"></i><span><strong>${t('How to apply:')} </strong>${esc(opt.application_method)}</span></div>` : ''}
          ${opt.timing           ? `<div class="chemical-detail"><i class="bi bi-clock"  aria-hidden="true"></i><span><strong>${t('When to apply:')} </strong>${esc(opt.timing)}</span></div>` : ''}
          ${opt.precautions      ? `<div class="chemical-detail chemical-precautions"><i class="bi bi-exclamation-triangle" aria-hidden="true"></i><span>${esc(opt.precautions)}</span></div>` : ''}
        </div>`).join('');
      chemHtml = `<p class="assessment-chemical-context">${t('Specific active ingredients recommended by AI for this disease. Always confirm with your local KVK or agronomist before purchase. Follow the current product label for dosage, dilution, and safety.')}</p>` + chemHtml;
    } else {
      chemHtml = `<p>${t('A specific chemical recommendation cannot be made from this assessment. Confirm the crop and cause with an expert first — a spray may not be needed or appropriate.')}</p>`;
    }

    /* Spray schedule */
    let sprayHtml = '';
    if (r.spray_schedule && r.spray_schedule.length) {
      sprayHtml = `
        <div class="spray-schedule">
          <h4><i class="bi bi-calendar3" aria-hidden="true"></i> ${t('Spray schedule')}</h4>
          <ol>${olli(r.spray_schedule)}</ol>
        </div>`;
    }

    /* Resistance management */
    let resistHtml = '';
    if (r.resistance_management && r.resistance_management.length) {
      resistHtml = `
        <div class="resistance-management">
          <h4><i class="bi bi-arrow-repeat" aria-hidden="true"></i> ${t('Resistance management')}</h4>
          <ul>${li(r.resistance_management)}</ul>
        </div>`;
    }

    /* Immediate actions */
    const immItems = (r.immediate_actions && r.immediate_actions.length)
      ? olli(r.immediate_actions)
      : `<li>${t('Capture a clearer leaf photo and confirm the cause with a local agricultural expert before treating.')}</li>`;

    resultEl.innerHTML = `
      <article class="disease-result" id="assessment-result" tabindex="-1" aria-labelledby="assessment-title">

        <header class="assessment-summary ${esc(r.status)}">
          <div class="assessment-top">
            <span class="eyebrow">${t('GEMINI · AI PHOTO ASSESSMENT')}</span>
            <span class="assessment-state">${statusLabel(r.status)}</span>
          </div>
          <p class="assessment-plant">${esc(r.plant || '')}</p>
          <h2 id="assessment-title">${esc(r.disease || '')}</h2>
          ${diseaseTypeBadge(r.disease_type)}
          <p>${esc(r.summary || '')}</p>
          <div class="assessment-certainty">
            <i class="bi bi-info-circle" aria-hidden="true"></i>
            <span>${t('Visual evidence strength:')} ${certaintyLabel} · ${t('AI estimate, not a measured accuracy score or confirmed diagnosis.')}</span>
          </div>
        </header>

        ${r.disease_description ? `
        <section class="assessment-section assessment-description">
          <span class="assessment-number"><i class="bi bi-book" aria-hidden="true"></i></span>
          <div><h3>${t('About this disease')}</h3><p>${esc(r.disease_description)}</p></div>
        </section>` : ''}

        ${section('01', t('Symptoms'), 'ul', r.symptoms)}
        ${section('02', t('What is visible in the photo'), 'ul', r.observations)}
        ${section('03', t('Other possible causes to check'), 'ul', r.possible_causes)}

        <section class="assessment-section assessment-urgent">
          <span class="assessment-number"><i class="bi bi-exclamation-circle" aria-hidden="true"></i></span>
          <div>
            <h3>${t('Immediate actions — do this now')}</h3>
            <ol>${immItems}</ol>
          </div>
        </section>

        ${section('04', t('Cultural control measures'), 'ul', r.cultural_control)}

        ${(r.biological_control && r.biological_control.length) ? `
        <section class="assessment-section assessment-bio">
          <span class="assessment-number"><i class="bi bi-tree" aria-hidden="true"></i></span>
          <div>
            <h3>${t('Biological & organic control')}</h3>
            <ul>${li(r.biological_control)}</ul>
          </div>
        </section>` : ''}

        <section class="assessment-section assessment-chemicals">
          <span class="assessment-number"><i class="bi bi-shield-check" aria-hidden="true"></i></span>
          <div>
            <h3>${t('Pesticide & spray recommendations')}</h3>
            ${chemHtml}
            ${sprayHtml}
            ${resistHtml}
            <p class="assessment-label-rule">${t('Use only a product currently approved for the confirmed crop and target. Follow its label for dose, dilution, protective equipment, re-entry interval, and the waiting period before harvest.')}</p>
            <a href="https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2146917&lang=2&reg=48" target="_blank" rel="noopener noreferrer">${t('Government guidance on pesticide label use')} ↗</a>
          </div>
        </section>

        ${section('05', t('Prevent spread and future recurrence'), 'ul', r.prevention)}
        ${section('06', t('What to check next'), 'ol', r.follow_up)}

        <footer class="assessment-footer">
          <i class="bi bi-journal-check" aria-hidden="true"></i>
          <p>${t('This is an AI-generated photo assessment, not a field or laboratory diagnosis. Confirm important treatment decisions with your local Krishi Vigyan Kendra (KVK) or a certified agronomist before applying any pesticide.')}</p>
        </footer>
      </article>`;
  }
})();
