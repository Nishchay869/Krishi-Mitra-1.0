(() => {
  try { localStorage.setItem('krishi-language', document.documentElement.lang); } catch { /* storage unavailable */ }
  const notice = document.getElementById('connection-status');
  const refresh = () => { if (notice) notice.hidden = navigator.onLine; };
  window.addEventListener('online', refresh);
  window.addEventListener('offline', refresh);
  refresh();
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js', { scope: '/', updateViaCache: 'none' })
        .then(registration => registration.update()).catch(() => { /* Optional offline enhancement. */ });
    });
  }
})();
