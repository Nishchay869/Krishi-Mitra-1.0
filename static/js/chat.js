// Shared chat client for the floating widget and the full chat page: typed questions, a hands-free
// live voice conversation (like Gemini Live), and spoken replies (female voice, volume-boosted).
(function () {
  const MAX_RECORDING_MS = 28000; // Sarvam speech-to-text rejects audio over 30 s
  const LOUDNESS_BOOST = 2.0; // pre-gain before a limiter: louder without clipping
  const AUTOPLAY_KEY = 'krishi-voice-autoplay';
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  // --- Spoken replies ------------------------------------------------------------------------
  const speech = {
    ctx: null, output: null, meter: null, current: null, token: 0, button: null,

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
        this.meter = this.ctx.createAnalyser(); // lets the live view move with the assistant's voice
        this.meter.fftSize = 1024;
        limiter.connect(this.meter);
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
      if (this.button) this.button.innerHTML = '<i class="bi bi-volume-up-fill"></i> ' + gettext('Listen');
      this.button = button;
      if (button) button.innerHTML = '<i class="bi bi-stop-fill"></i> ' + gettext('Stop');
    },

    // Speak a stored bot reply (fetched from the server by message id).
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
        await this.playQueued((await res.json()).audios || [], token);
      } catch (err) { /* speech is optional; the text reply is already shown */ }
      if (token === this.token) { this.current = null; this.setButton(null); }
    },

    // Play base64 MP3 clips (e.g. the greeting), replacing anything currently speaking.
    async playClips(clips) {
      this.unlock();
      if (!this.ctx) return;
      this.stop();
      await this.playQueued(clips, this.token);
    },

    // Play clips in order; stops early once stop() changes the token.
    async playQueued(clips, token) {
      try {
        for (const clip of clips) {
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
      } catch (err) { /* undecodable clip: skip the audio */ }
      if (token === this.token) this.current = null;
    },
  };

  function addListenButton(bubble, messageId) {
    if (!speech.enabled() || !messageId) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm btn-link listen-btn p-0 mt-1';
    btn.innerHTML = '<i class="bi bi-volume-up-fill"></i> ' + gettext('Listen');
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
      src.textContent = `${gettext('Source:')} ${source}`;
      if (sourceUrl) { src.href = sourceUrl; src.target = '_blank'; src.rel = 'noopener'; }
      div.appendChild(src);
    }
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  }

  const logFor = (form) => form.closest('[data-chat-root], #chat-widget').querySelector('[data-chat-log]');

  async function ask(log, request) {
    const typing = addBubble(log, gettext("Thinking…"), 'bot typing');
    try {
      const res = await fetch(request.url, {
        method: 'POST', headers: { 'X-CSRFToken': csrf(), ...request.headers }, body: request.body,
      });
      const data = await res.json();
      typing.remove();
      return data;
    } catch (err) {
      typing.remove();
      return { error: gettext("Network error. Please try again.") };
    }
  }

  function showReply(log, data) {
    if (data.translation_unavailable) addBubble(log, gettext('Translation is temporarily unavailable. This answer is shown in English.'), 'bot');
    const bubble = addBubble(log, data.reply || data.error || gettext("Something went wrong."), 'bot', data.source, data.source_url);
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

  const widget = document.getElementById('chat-widget');
  const toggle = document.getElementById('chat-toggle');

  // --- Live voice conversation (tap mic once; listen → answer → speak → listen …) -------------
  const SILENCE_TO_SEND_MS = 1200;   // pause that ends a question
  const MIN_SPEECH_MS = 300;         // ignore coughs and clicks
  const NO_SPEECH_PAUSE_MS = 15000;  // stop listening (and spending nothing) after 15 s of silence
  const MIN_THRESHOLD = 0.015;       // RMS level that counts as speech, raised automatically in noisy places

  const DICTATION_NO_SPEECH_MS = 8000;

  // Open the microphone with an analyser for voice-activity detection. Throws if access is denied.
  async function openMic() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder || !speech.ctx) throw new Error('unsupported');
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });
    const analyser = speech.ctx.createAnalyser();
    analyser.fftSize = 1024;
    speech.ctx.createMediaStreamSource(stream).connect(analyser);
    return { stream, analyser, close: () => stream.getTracks().forEach((t) => t.stop()) };
  }

  const audioFilename = (blob) => `speech.${blob.type.includes('mp4') ? 'm4a' : blob.type.includes('ogg') ? 'ogg' : 'webm'}`;

  // Record one utterance: starts on voice, stops after a pause.
  // Returns { done: Promise<Blob|null>, cancel(), sendNow() }; done is null if nobody spoke.
  function recordSpeech(mic, { onLevel, noSpeechMs }) {
    const recorder = new MediaRecorder(mic.stream);
    const chunks = [];
    const samples = new Float32Array(mic.analyser.fftSize);
    const startedAt = performance.now();
    let noise = 0.005, spokenMs = 0, speaking = false, silenceSince = null, last = startedAt, send = false, timer;

    const done = new Promise((resolve) => {
      recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
      recorder.onstop = () => resolve(send && chunks.length ? new Blob(chunks, { type: recorder.mimeType || 'audio/webm' }) : null);
    });
    const finish = (shouldSend) => {
      clearInterval(timer);
      send = shouldSend;
      if (recorder.state !== 'inactive') recorder.stop();
    };

    timer = setInterval(() => {
      const now = performance.now();
      const dt = now - last;
      last = now;
      mic.analyser.getFloatTimeDomainData(samples);
      const rms = Math.sqrt(samples.reduce((sum, v) => sum + v * v, 0) / samples.length);
      const threshold = Math.max(MIN_THRESHOLD, noise * 3);
      onLevel?.(rms / threshold);

      if (rms > threshold) {
        speaking = true;
        spokenMs += dt;
        silenceSince = null;
      } else {
        noise = noise * 0.95 + rms * 0.05; // learn the background noise level
        if (speaking) {
          silenceSince ??= now;
          if (now - silenceSince > SILENCE_TO_SEND_MS) {
            if (spokenMs >= MIN_SPEECH_MS) return finish(true);
            speaking = false; spokenMs = 0; silenceSince = null; // too short: keep listening
          }
        }
      }
      if (!speaking && spokenMs === 0 && now - startedAt > noSpeechMs) return finish(false);
      if (now - startedAt > MAX_RECORDING_MS) return finish(spokenMs >= MIN_SPEECH_MS);
    }, 50);
    recorder.start();
    return { done, cancel: () => finish(false), sendNow: () => finish(spokenMs >= MIN_SPEECH_MS) };
  }

  const live = {
    active: false, mic: null, log: null, el: null, resumeTap: null, cancel: null, sendNow: null,
    unmountStrands: null, speakingMeter: null,

    // Returns true if the conversation started; false means use the text chat instead.
    async start(form) {
      if (this.active) return true;
      this.form = form;
      this.log = logFor(form);
      speech.unlock();
      speech.stop();
      try {
        this.mic = await openMic();
      } catch (err) {
        addBubble(this.log, err.message === 'unsupported'
          ? gettext("Voice conversation is not supported in this browser. Please type your question.")
          : gettext("Microphone access was blocked. Allow it in the browser settings to talk to the assistant."), 'bot');
        return false;
      }
      this.active = true;
      this.overlay().classList.remove('d-none');
      document.body.classList.add('overflow-hidden');
      this.startVisuals();
      this.run();
      return true;
    },

    // Leave voice mode and continue the same conversation by typing.
    typeInstead() {
      this.end();
      if (widget && this.form && widget.contains(this.form)) openWidget();
      this.form?.elements.message.focus();
    },

    end() {
      if (!this.active) return;
      this.active = false;
      this.cancel?.();
      this.resumeTap?.();
      speech.stop();
      this.mic?.close();
      this.mic = null;
      this.stopVisuals();
      this.el.classList.add('d-none');
      document.body.classList.remove('overflow-hidden');
    },

    // Spoken welcome: "Good morning, <name>! I'm Krishi Mitra…" in the farmer's preferred language.
    async greet() {
      if (!window.CHAT_GREETING_URL) return;
      this.show('thinking', gettext("Namaste! 🙏"), '', '');
      let data;
      try {
        const res = await fetch(window.CHAT_GREETING_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
          body: JSON.stringify({ hour: new Date().getHours() }),
        });
        data = await res.json();
      } catch (err) {
        return; // no greeting; go straight to listening
      }
      if (!this.active || !data.text) return;
      addBubble(this.log, data.text, 'bot');
      this.show('speaking', gettext("Speaking… tap the circle to skip"), '', data.text);
      await speech.playClips(data.audios || []);
    },

    async run() {
      await this.greet();
      while (this.active) {
        this.show('listening', gettext("Listening…"));
        const audio = await this.capture();
        if (!this.active) break;
        if (!audio) {
          this.show('paused', gettext("Paused — tap the circle to talk"));
          await new Promise((resolve) => { this.resumeTap = resolve; });
          this.resumeTap = null;
          continue;
        }

        this.show('thinking', gettext("Thinking…"));
        const body = new FormData();
        body.append('audio', audio, audioFilename(audio));
        const data = await ask(this.log, { url: window.CHAT_VOICE_URL, headers: {}, body });
        if (!this.active) break;
        if (!data.reply) {
          this.show('listening', data.error || gettext("Sorry, I didn't catch that."), '', '');
          await new Promise((r) => setTimeout(r, 1500));
          continue;
        }

        addBubble(this.log, `🎤 ${data.transcript}`, 'user');
        const bubble = addBubble(this.log, data.reply, 'bot', data.source, data.source_url);
        const btn = addListenButton(bubble, data.message_id);
        this.show('speaking', gettext("Speaking… tap the circle to interrupt"), data.transcript, data.reply);
        await speech.play(data.message_id, btn);
      }
    },

    capture() {
      const rec = recordSpeech(this.mic, { onLevel: (v) => this.level(v), noSpeechMs: NO_SPEECH_PAUSE_MS });
      this.cancel = rec.cancel;
      this.sendNow = rec.sendNow; // tap while talking in a noisy place
      return rec.done.finally(() => { this.cancel = null; this.sendNow = null; });
    },

    show(state, status, heard, reply) {
      const el = this.overlay();
      el.dataset.state = state;
      window.dispatchEvent(new CustomEvent('krishi:live', { detail: { state } }));
      el.querySelector('.live-status').textContent = status;
      if (heard !== undefined) el.querySelector('.live-heard').textContent = heard ? `“${heard}”` : '';
      if (reply !== undefined) el.querySelector('.live-reply').textContent = reply;
      this.level(0);
    },

    level(value) {
      // Feed the Strands animation via krishi:live events (orb removed).
      window.dispatchEvent(new CustomEvent('krishi:live', { detail: { level: Math.min(1, value / 3) } }));
    },

    // React Bits "Strands" background (frontend/src/islands/LiveStrands.tsx), mounted only while
    // the conversation is open so the WebGL animation never runs in the background.
    startVisuals() {
      const host = this.el.querySelector('.live-strands');
      window.KrishiIslands?.mount(host, 'LiveStrands').then((unmount) => {
        if (this.active) this.unmountStrands = unmount; else unmount();
      }).catch(() => { /* decorative only */ });
      const samples = new Float32Array(1024);
      this.speakingMeter = setInterval(() => {
        if (this.el.dataset.state !== 'speaking' || !speech.meter) return;
        speech.meter.getFloatTimeDomainData(samples);
        const rms = Math.sqrt(samples.reduce((sum, v) => sum + v * v, 0) / samples.length);
        this.level(rms / 0.05);
      }, 50);
    },

    stopVisuals() {
      clearInterval(this.speakingMeter);
      this.unmountStrands?.();
      this.unmountStrands = null;
    },


    overlay() {
      if (this.el) return this.el;
      const el = document.createElement('div');
      el.className = 'live-overlay d-none';
      el.setAttribute('role', 'dialog');
      el.setAttribute('aria-modal', 'true');
      el.setAttribute('aria-label', gettext("Live voice conversation"));
      el.innerHTML = `
        <div class="live-strands" aria-hidden="true"></div>
        <div class="live-title"><i class="bi bi-flower1"></i> ${gettext("Krishi Mitra · Live")}</div>
        <div class="live-status" aria-live="polite"></div>
        <div class="live-heard"></div>
        <div class="live-reply"></div>
        <div class="live-hint">${gettext("Speak in any language. Pause when you finish — I'll answer and then listen again.")}</div>
        <div class="d-flex gap-2">
          <button type="button" class="btn btn-outline-light btn-lg rounded-pill live-type"><i class="bi bi-keyboard"></i> ${gettext("Type instead")}</button>
          <button type="button" class="btn btn-danger btn-lg rounded-pill live-end"><i class="bi bi-x-lg"></i> ${gettext("End")}</button>
        </div>`;
      el.querySelector('.live-type').addEventListener('click', () => this.typeInstead());
      el.querySelector('.live-end').addEventListener('click', () => this.end());
      document.addEventListener('keydown', (e) => e.key === 'Escape' && this.end());
      document.body.appendChild(el);
      this.el = el;
      return el;
    },
  };

  // --- Dictation: the 🎤 in the typing bar turns speech into text in the box (nothing is sent) ----
  const dictation = {
    rec: null,

    async toggle(button, form) {
      if (this.rec) { this.rec.sendNow(); return; } // second tap = "I'm done"
      const input = form.elements.message;
      speech.unlock();
      speech.stop();
      let mic;
      try {
        mic = await openMic();
      } catch (err) {
        this.flash(input, err.message === 'unsupported' ? gettext("Voice typing is not supported in this browser.")
          : gettext("Microphone blocked — allow it in browser settings."));
        return;
      }
      this.rec = recordSpeech(mic, {
        onLevel: (v) => button.style.setProperty('--level', Math.min(1, v / 3).toFixed(2)),
        noSpeechMs: DICTATION_NO_SPEECH_MS,
      });
      this.ui(button, input, 'recording');
      const audio = await this.rec.done;
      this.rec = null;
      mic.close();
      if (!audio) { this.ui(button, input, 'idle'); return; }

      this.ui(button, input, 'converting');
      let data;
      try {
        const body = new FormData();
        body.append('audio', audio, audioFilename(audio));
        const res = await fetch(window.CHAT_TRANSCRIBE_URL, { method: 'POST', headers: { 'X-CSRFToken': csrf() }, body });
        data = await res.json();
      } catch (err) {
        data = { error: gettext("Network error. Please try again.") };
      }
      this.ui(button, input, 'idle');
      if (data.transcript) {
        input.value = input.value.trim() ? `${input.value.trim()} ${data.transcript}` : data.transcript;
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      } else {
        this.flash(input, data.error || gettext("Couldn't hear that. Please try again."));
      }
    },

    ui(button, input, state) {
      const recording = state === 'recording';
      button.classList.toggle('btn-danger', recording);
      button.classList.toggle('recording', recording);
      button.classList.toggle('btn-outline-secondary', !recording);
      button.disabled = state === 'converting';
      input.disabled = state === 'converting';
      button.innerHTML = recording ? '<i class="bi bi-stop-fill"></i>'
        : state === 'converting' ? '<span class="spinner-border spinner-border-sm"></span>' : '<i class="bi bi-mic-fill"></i>';
      button.title = recording ? gettext("Done speaking") : gettext("Dictate: speak and the words appear in the box");
      input.placeholder = recording ? gettext("Listening… speak, then pause or tap ■")
        : state === 'converting' ? gettext("Converting your speech to text…") : input.form.dataset.placeholder;
      if (!recording) button.style.removeProperty('--level');
    },

    flash(input, message) {
      input.placeholder = message;
      setTimeout(() => { input.placeholder = input.form.dataset.placeholder; }, 3500);
    },
  };

  document.querySelectorAll('[data-chat-form]').forEach((form) => {
    form.dataset.placeholder = form.elements.message.placeholder;
    form.addEventListener('submit', (e) => { e.preventDefault(); sendText(form); });
    const mic = form.querySelector('[data-mic]');
    if (mic) mic.addEventListener('click', () => dictation.toggle(mic, form));
  });

  // Voice on/off switches (header of chat page and widget) and Listen buttons on saved history.
  document.querySelectorAll('[data-voice-toggle]').forEach((toggleBtn) => {
    const render = () => {
      const on = speech.autoplay();
      toggleBtn.innerHTML = on ? '<i class="bi bi-volume-up-fill"></i>' : '<i class="bi bi-volume-mute-fill"></i>';
      toggleBtn.title = on ? gettext("Voice replies on (tap to mute)") : gettext("Voice replies off (tap to turn on)");
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

  // Floating Farm Assistant button: opens the live voice conversation directly (text chat if voice
  // is unavailable or the microphone is blocked; "${gettext("Type instead")}" in the live view also opens it).
  function openWidget() {
    const log = widget.querySelector('[data-chat-log]');
    widget.classList.remove('d-none');
    if (!log.childElementCount) addBubble(log, gettext("Namaste! Ask me about crops, fertilizers, pests or government schemes — type or speak in your own language."), 'bot');
    widget.querySelector('input').focus();
  }

  const pageForm = document.querySelector('[data-chat-root] [data-chat-form]');
  if (toggle && !widget && pageForm) {
    toggle.addEventListener('click', () => live.start(pageForm)); // Ask Assistant page
  }
  if (widget && toggle) {
    toggle.addEventListener('click', async () => {
      if (!widget.classList.contains('d-none')) { widget.classList.add('d-none'); return; }
      if (!speech.enabled() || !(await live.start(widget.querySelector('[data-chat-form]')))) openWidget();
    });
    document.getElementById('chat-close').addEventListener('click', () => widget.classList.add('d-none'));
  }
})();
