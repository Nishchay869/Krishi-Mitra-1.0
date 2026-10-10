// Shared chat client for the floating widget and the full chat page: typed and voice questions.
(function () {
  const MAX_RECORDING_MS = 30000;
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

  const logFor = (form) => form.closest('[data-chat-root], #chat-widget').querySelector('[data-chat-log]');

  async function ask(log, request) {
    const typing = addBubble(log, 'Thinking…', 'bot typing');
    try {
      const res = await fetch(request.url, {
        method: 'POST', headers: { 'X-CSRFToken': csrf(), ...request.headers }, body: request.body,
      });
      const data = await res.json();
      typing.remove();
      return data;
    } catch (err) {
      typing.remove();
      return { error: 'Network error. Please try again.' };
    }
  }

  function showReply(log, data) {
    addBubble(log, data.reply || data.error || 'Something went wrong.', 'bot', data.source, data.source_url);
  }

  async function sendText(form) {
    const log = logFor(form);
    const input = form.elements.message;
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addBubble(log, text, 'user');
    showReply(log, await ask(log, {
      url: window.CHAT_API_URL,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    }));
  }

  // --- Voice input -------------------------------------------------------------------------
  let recorder = null;

  async function toggleRecording(button, form) {
    if (recorder) { recorder.stop(); return; }
    const log = logFor(form);
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      addBubble(log, 'Voice input is not supported in this browser. Please type your question.', 'bot');
      return;
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      addBubble(log, 'Microphone access was blocked. Allow it in the browser settings to ask by voice.', 'bot');
      return;
    }

    const chunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    const timer = setTimeout(() => recorder?.state === 'recording' && recorder.stop(), MAX_RECORDING_MS);
    recorder.onstop = async () => {
      clearTimeout(timer);
      stream.getTracks().forEach((t) => t.stop());
      const type = recorder.mimeType || 'audio/webm';
      recorder = null;
      setRecordingUI(button, form, false);
      if (!chunks.length) return;

      const ext = type.includes('mp4') ? 'm4a' : type.includes('ogg') ? 'ogg' : 'webm';
      const body = new FormData();
      body.append('audio', new Blob(chunks, { type }), `question.${ext}`);
      const data = await ask(log, { url: window.CHAT_VOICE_URL, headers: {}, body });
      if (data.transcript) addBubble(log, `🎤 ${data.transcript}`, 'user');
      showReply(log, data);
    };
    recorder.start();
    setRecordingUI(button, form, true);
  }

  function setRecordingUI(button, form, recording) {
    button.classList.toggle('btn-danger', recording);
    button.classList.toggle('btn-outline-secondary', !recording);
    button.innerHTML = recording ? '<i class="bi bi-stop-fill"></i>' : '<i class="bi bi-mic-fill"></i>';
    button.title = recording ? 'Stop and send' : 'Ask by voice';
    form.elements.message.placeholder = recording ? 'Listening… speak in your language, tap ■ to send' : form.dataset.placeholder;
  }

  document.querySelectorAll('[data-chat-form]').forEach((form) => {
    form.dataset.placeholder = form.elements.message.placeholder;
    form.addEventListener('submit', (e) => { e.preventDefault(); sendText(form); });
    const mic = form.querySelector('[data-mic]');
    if (mic) mic.addEventListener('click', () => toggleRecording(mic, form));
  });

  const widget = document.getElementById('chat-widget');
  const toggle = document.getElementById('chat-toggle');
  if (widget && toggle) {
    const log = widget.querySelector('[data-chat-log]');
    toggle.addEventListener('click', () => {
      widget.classList.toggle('d-none');
      if (!log.childElementCount) addBubble(log, 'Namaste! Ask me about crops, fertilizers, pests or government schemes — type or speak in your own language.', 'bot');
      widget.querySelector('input').focus();
    });
    document.getElementById('chat-close').addEventListener('click', () => widget.classList.add('d-none'));
  }
})();
