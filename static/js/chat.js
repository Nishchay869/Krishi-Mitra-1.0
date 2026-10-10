// Shared chat client for the floating widget and the full chat page: typed and voice questions,
// plus spoken replies (female voice, volume-boosted for noisy fields).
(function () {
  const MAX_RECORDING_MS = 30000;
  const LOUDNESS_BOOST = 2.0; // pre-gain before a limiter: louder without clipping
  const AUTOPLAY_KEY = 'krishi-voice-autoplay';
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  // --- Spoken replies ------------------------------------------------------------------------
  const speech = {
    ctx: null, output: null, current: null, token: 0, button: null,

    enabled: () => Boolean(window.CHAT_SPEAK_URL),
    autoplay() {
      try { return localStorage.getItem(AUTOPLAY_KEY) !== '0'; } catch (e) { return true; }
    },
    setAutoplay(on) {
      try { localStorage.setItem(AUTOPLAY_KEY, on ? '1' : '0'); } catch (e) { /* storage blocked */ }
      if (!on) this.stop();
    },

    // Must be called from a click/submit so browsers allow sound.
    unlock() {
      if (!this.enabled()) return;
      if (!this.ctx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        this.ctx = new Ctx();
        const gain = this.ctx.createGain();
        gain.gain.value = LOUDNESS_BOOST;
        const limiter = this.ctx.createDynamicsCompressor();
        limiter.threshold.value = -6; limiter.knee.value = 6; limiter.ratio.value = 20;
        limiter.attack.value = 0.003; limiter.release.value = 0.2;
        gain.connect(limiter).connect(this.ctx.destination);
        this.output = gain;
      }
      if (this.ctx.state === 'suspended') this.ctx.resume();
    },

    stop() {
      this.token += 1;
      try { this.current?.stop(); } catch (e) { /* already stopped */ }
      this.current = null;
      this.setButton(null);
    },

    setButton(button) {
      if (this.button) this.button.innerHTML = '<i class="bi bi-volume-up-fill"></i> Listen';
      this.button = button;
      if (button) button.innerHTML = '<i class="bi bi-stop-fill"></i> Stop';
    },

    async play(messageId, button) {
      this.unlock();
      if (!this.ctx) return;
      this.stop();
      const token = this.token;
      this.setButton(button);
      try {
        const res = await fetch(window.CHAT_SPEAK_URL.replace('/0/', `/${messageId}/`), {
          method: 'POST', headers: { 'X-CSRFToken': csrf() },
        });
        const data = await res.json();
        for (const clip of data.audios || []) {
          if (token !== this.token) return;
          const bytes = Uint8Array.from(atob(clip), (c) => c.charCodeAt(0));
          const buffer = await this.ctx.decodeAudioData(bytes.buffer);
          if (token !== this.token) return;
          await new Promise((resolve) => {
            const src = this.ctx.createBufferSource();
            src.buffer = buffer;
            src.connect(this.output);
            src.onended = resolve;
            this.current = src;
            src.start();
          });
        }
      } catch (err) { /* speech is optional; the text reply is already shown */ }
      if (token === this.token) { this.current = null; this.setButton(null); }
    },
  };

  function addListenButton(bubble, messageId) {
    if (!speech.enabled() || !messageId) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm btn-link listen-btn p-0 mt-1';
    btn.innerHTML = '<i class="bi bi-volume-up-fill"></i> Listen';
    btn.addEventListener('click', () => (speech.button === btn ? speech.stop() : speech.play(messageId, btn)));
    bubble.appendChild(btn);
    return btn;
  }

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
    const bubble = addBubble(log, data.reply || data.error || 'Something went wrong.', 'bot', data.source, data.source_url);
    const btn = addListenButton(bubble, data.message_id);
    if (btn && speech.autoplay()) speech.play(data.message_id, btn);
  }

  async function sendText(form) {
    const log = logFor(form);
    const input = form.elements.message;
    const text = input.value.trim();
    if (!text) return;
    speech.unlock();
    speech.stop();
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
    speech.unlock();
    speech.stop(); // never record the assistant's own voice
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

  // Voice on/off switches (header of chat page and widget) and Listen buttons on saved history.
  document.querySelectorAll('[data-voice-toggle]').forEach((toggleBtn) => {
    const render = () => {
      const on = speech.autoplay();
      toggleBtn.innerHTML = on ? '<i class="bi bi-volume-up-fill"></i>' : '<i class="bi bi-volume-mute-fill"></i>';
      toggleBtn.title = on ? 'Voice replies on (tap to mute)' : 'Voice replies off (tap to turn on)';
      toggleBtn.setAttribute('aria-pressed', String(on));
    };
    render();
    toggleBtn.addEventListener('click', () => {
      speech.setAutoplay(!speech.autoplay());
      document.querySelectorAll('[data-voice-toggle]').forEach((b) => b.dispatchEvent(new Event('voice:render')));
    });
    toggleBtn.addEventListener('voice:render', render);
  });
  document.querySelectorAll('.bubble.bot[data-message-id]').forEach((b) => addListenButton(b, b.dataset.messageId));

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
