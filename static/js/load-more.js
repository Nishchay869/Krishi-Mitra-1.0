/* Pagination: "Load more" appends the next page of a list, and loads automatically when the
   button scrolls into view.

   Markup (server renders one page; the link is a normal next-page link without JavaScript):
     <div id="items"> ...items... </div>
     <div data-load-more="#items"><a href="?page=2" data-load-more-link>Load more</a></div>

   The next page is fetched, its items (children of the same #items element, except the
   load-more block) are appended, and the load-more block is replaced by the next page's one
   (or removed on the last page). Fires "load-more:appended" on the list. */
(() => {
  const loading = new WeakSet();
  const observed = new WeakSet();

  async function loadMore(block) {
    const link = block.querySelector('[data-load-more-link]');
    const list = document.querySelector(block.dataset.loadMore);
    if (!link || !list || loading.has(block)) return;
    loading.add(block);
    link.setAttribute('aria-busy', 'true');
    link.classList.add('is-loading');
    try {
      const resp = await fetch(link.href, { headers: { 'X-Requested-With': 'fetch' } });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const doc = new DOMParser().parseFromString(await resp.text(), 'text/html');
      const freshList = doc.querySelector(block.dataset.loadMore);
      if (!freshList) throw new Error('list missing on next page');
      const items = [...freshList.children].filter((el) => !el.matches('[data-load-more]'));
      const nextBlock = doc.querySelector(`[data-load-more="${block.dataset.loadMore}"]`);
      if (block.parentElement === list) items.forEach((el) => list.insertBefore(el, block));
      else list.append(...items);
      if (nextBlock) {
        block.replaceWith(nextBlock);
        watch(nextBlock);
      } else {
        block.remove();
      }
      list.dispatchEvent(new CustomEvent('load-more:appended', { bubbles: true, detail: { items } }));
    } catch (err) {
      window.location.href = link.href; // fall back to opening the next page normally
    } finally {
      loading.delete(block);
    }
  }

  // Load automatically when the button comes near the screen (infinite scroll).
  const observer = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) loadMore(e.target);
    }), { rootMargin: '400px 0px' })
    : null;

  function watch(block) {
    if (observed.has(block)) return;
    observed.add(block);
    block.querySelector('[data-load-more-link]')?.addEventListener('click', (event) => {
      event.preventDefault();
      loadMore(block);
    });
    observer?.observe(block);
  }

  // Backup for fast flings: the observer only fires when the block is seen during a frame, so
  // a big jump past it would never load. Also load when the block is near or above the screen.
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      document.querySelectorAll('[data-load-more]').forEach((block) => {
        if (block.getBoundingClientRect().top < window.innerHeight + 400) loadMore(block);
      });
    });
  }, { passive: true });

  const init = () => document.querySelectorAll('[data-load-more]').forEach(watch);
  init();
  document.addEventListener('live-search:updated', init); // live search swaps in a fresh page 1
})();
