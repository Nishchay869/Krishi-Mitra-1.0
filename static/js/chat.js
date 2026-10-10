// Shared chat client for the floating widget and the full chat page.
(function () {
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  function addBubble(log, text, who, source, sourceUrl) {
    const div = document.createElement('div');
    div.className = `bubble ${who}`;
    div.textContent = text;
    if (source) {
      const src = document.createElement(sourceUrl ? 'a' : 'span');
      src.className = 'source';
      src.textContent = `Source: ${source}`;
      if (sourceUrl) { src.href = sourceUrl; src.target = '_blank'; src.rel = 'noopener'; }
      div.appendChild(src);
    }
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  }

  async function send(form) {
    const log = form.closest('[data-chat-root], #chat-widget').querySelector('[data-chat-log]');
    const input = form.elements.message;
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addBubble(log, text, 'user');
    const typing = addBubble(log, 'Thinking…', 'bot typing');
    try {
      const res = await fetch(window.CHAT_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      typing.remove();
      addBubble(log, data.reply || data.error || 'Something went wrong.', 'bot', data.source, data.source_url);
    } catch (err) {
      typing.remove();
      addBubble(log, 'Network error. Please try again.', 'bot');
    }
  }

  document.querySelectorAll('[data-chat-form]').forEach((form) => {
    form.addEventListener('submit', (e) => { e.preventDefault(); send(form); });
  });

  const widget = document.getElementById('chat-widget');
  const toggle = document.getElementById('chat-toggle');
  if (widget && toggle) {
    const log = widget.querySelector('[data-chat-log]');
    toggle.addEventListener('click', () => {
      widget.classList.toggle('d-none');
      if (!log.childElementCount) addBubble(log, 'Namaste! Ask me about crops, fertilizers, pests or government schemes.', 'bot');
      widget.querySelector('input').focus();
    });
    document.getElementById('chat-close').addEventListener('click', () => widget.classList.add('d-none'));
  }
})();
