// Native details remain readable and keyboard accessible without this enhancement.
(() => {
  const guide = document.getElementById('cultivation-tips');
  if (!guide) return;
  const topics = Array.from(guide.querySelectorAll('.cultivation-topic'));
  const controls = guide.querySelector('.cultivation-controls');
  if (controls) controls.hidden = false;
  guide.querySelector('[data-cultivation-expand]')?.addEventListener('click', () => {
    topics.forEach(topic => { topic.open = true; });
  });
  guide.querySelector('[data-cultivation-collapse]')?.addEventListener('click', () => {
    topics.forEach(topic => { topic.open = false; });
  });
  const openHash = () => {
    const target = topics.find(topic => `#${topic.id}` === window.location.hash);
    if (target) target.open = true;
  };
  guide.querySelectorAll('.cultivation-navigation a').forEach(link => {
    link.addEventListener('click', () => {
      const target = topics.find(topic => `#${topic.id}` === link.getAttribute('href'));
      if (target) target.open = true;
    });
  });
  window.addEventListener('hashchange', openHash);
  openHash();
})();
