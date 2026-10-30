/* A small progressive enhancement: forms work even when JavaScript is disabled. */
(() => {
  const slides = [...document.querySelectorAll('[data-slide]')];
  if (!slides.length) return;
  const dots = [...document.querySelectorAll('[data-dot]')];
  const next = document.querySelector('[data-tour-next]');
  let current = 0;
  function show(index, focus = true) {
    current = index;
    slides.forEach((slide, i) => { slide.hidden = i !== index; });
    dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === index)));
    if (focus) slides[index].querySelector('h1').focus({preventScroll: true});
  }
  document.querySelector('.tour-dots').hidden = false;
  dots.forEach((dot, index) => dot.addEventListener('click', () => show(index)));
  next.addEventListener('click', event => {
    if (current < slides.length - 1) { event.preventDefault(); show(current + 1); }
  });
  show(0, false);
})();
