/* Live search: results update while typing, debounced, with autocomplete suggestions.

   Markup:
     <form method="get">
       <input type="search" name="q" data-live-search="#results-id">
     </form>
     <div id="results-id"> ...results; elements with [data-suggest] feed the autocomplete... </div>

   - Debounce: waits 300 ms after the last keystroke (no request per key press).
   - Only the newest search counts: an older, slower request is cancelled (AbortController).
   - The page asks the same URL the form would submit to and swaps in just the results
     region, so filters, translations and server-side logic stay exactly the same.
   - The address bar is updated (history.replaceState) so back/share/reload keep the search.
   - Without JavaScript, or if anything fails, the normal form submit still works. */
(() => {
  const DEBOUNCE_MS = 300;
  const MIN_CHARS = 2;          // 0 or 1 letter: wait (an empty box restores the full list)
  const MAX_SUGGESTIONS = 8;

  document.querySelectorAll('input[data-live-search]').forEach((input) => {
    const form = input.form;
    const selector = input.dataset.liveSearch;
    if (!form || !document.querySelector(selector)) return;

    // Autocomplete: a <datalist> filled from the [data-suggest] items in the results.
    const list = document.createElement('datalist');
    list.id = `${input.id || input.name}-suggestions`;
    input.setAttribute('list', list.id);
    input.after(list);
    const fillSuggestions = (root) => {
      const names = [...new Set([...root.querySelectorAll('[data-suggest]')]
        .map((el) => el.textContent.trim()).filter(Boolean))];
      list.replaceChildren(...names.slice(0, MAX_SUGGESTIONS).map((name) => {
        const option = document.createElement('option');
        option.value = name;
        return option;
      }));
    };
    fillSuggestions(document.querySelector(selector));

    let timer = null;
    let controller = null;
    let lastUrl = null;

    const search = async () => {
      const params = new URLSearchParams(new FormData(form));
      const url = `${form.getAttribute('action') || window.location.pathname}?${params}`;
      if (url === lastUrl) return;
      controller?.abort();
      controller = new AbortController();
      const results = document.querySelector(selector);
      results.setAttribute('aria-busy', 'true');
      results.classList.add('live-search-loading');
      try {
        const resp = await fetch(url, { signal: controller.signal, headers: { 'X-Requested-With': 'fetch' } });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const doc = new DOMParser().parseFromString(await resp.text(), 'text/html');
        const fresh = doc.querySelector(selector);
        if (!fresh) throw new Error('results region missing');
        results.innerHTML = fresh.innerHTML;
        lastUrl = url;
        window.history.replaceState(window.history.state, '', url);
        fillSuggestions(results);
        results.dispatchEvent(new CustomEvent('live-search:updated', { bubbles: true }));
      } catch (err) {
        if (err.name !== 'AbortError') form.submit(); // fall back to a normal search
      } finally {
        if (!controller.signal.aborted) {
          results.removeAttribute('aria-busy');
          results.classList.remove('live-search-loading');
        }
      }
    };

    input.addEventListener('input', () => {
      clearTimeout(timer);
      const length = input.value.trim().length;
      if (length > 0 && length < MIN_CHARS) return;
      timer = setTimeout(search, DEBOUNCE_MS);
    });
    // Enter: search right away instead of reloading the page.
    form.addEventListener('submit', (event) => {
      if (event.submitter && event.submitter !== input && event.submitter.name) return; // other buttons keep their behaviour
      event.preventDefault();
      clearTimeout(timer);
      search();
    });
  });
})();
