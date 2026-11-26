(() => {
  'use strict';

  const status = document.getElementById('accessibilityStatus');
  const speech = window.speechSynthesis;
  const voicePicker = document.getElementById('voicePicker');
  const voiceRate = document.getElementById('voiceRate');
  let availableVoices = [];
  let readingId = 0;
  let lastSpokenText = '';
  let currentScale = 1;
  try {
    currentScale = Number(localStorage.getItem('alfamx-text-scale') || '1');
  } catch (_) {
    currentScale = 1;
  }

  function announce(message) {
    if (status) status.textContent = message;
  }

  function voiceScore(voice) {
    const name = voice.name.toLowerCase();
    return (/^es-mx/i.test(voice.lang) ? 100 : /^es/i.test(voice.lang) ? 50 : 0)
      + (/natural|neural|online|google|microsoft|paulina|dalia|sabina|paloma|helena|alvaro/i.test(name) ? 25 : 0)
      + (voice.localService ? 2 : 0);
  }

  function updateVoices() {
    if (!speech) return;
    availableVoices = speech.getVoices().filter(voice => /^es(?:-|$)/i.test(voice.lang))
      .sort((a, b) => voiceScore(b) - voiceScore(a));
    if (!voicePicker) return;
    let savedVoice = '';
    try { savedVoice = localStorage.getItem('alfamx-voice') || ''; } catch (_) { /* Preferencia opcional. */ }
    voicePicker.replaceChildren(new Option('Voz automática (recomendada)', ''));
    availableVoices.forEach(voice => voicePicker.add(new Option(`${voice.name} (${voice.lang})`, voice.voiceURI)));
    voicePicker.value = availableVoices.some(voice => voice.voiceURI === savedVoice) ? savedVoice : '';
  }

  function splitForSpeech(text) {
    const sentences = text.match(/[^.!?;\n]+[.!?;]?/g) || [text];
    const chunks = [];
    let chunk = '';
    sentences.forEach(sentence => {
      const words = sentence.trim().split(/\s+/);
      words.forEach(word => {
        if (chunk.length + word.length + 1 > 160 && chunk) {
          chunks.push(chunk.trim());
          chunk = '';
        }
        chunk += (chunk ? ' ' : '') + word;
      });
    });
    if (chunk.trim()) chunks.push(chunk.trim());
    return chunks;
  }

  function speak(text) {
    const content = String(text || '').replace(/\s+/g, ' ').trim();
    if (!content) {
      announce('No encontré texto para escuchar en esta pantalla.');
      return;
    }
    if (!speech || typeof SpeechSynthesisUtterance === 'undefined') {
      announce('Este navegador no tiene lectura por voz. Prueba con Chrome o Edge actualizado.');
      return;
    }
    lastSpokenText = content;
    const thisReading = ++readingId;
    speech.cancel();
    updateVoices();
    const selected = availableVoices.find(v => v.voiceURI === voicePicker?.value) || availableVoices[0];
    const chunks = splitForSpeech(content);
    let index = 0;
    function nextChunk() {
      if (thisReading !== readingId) return;
      if (index >= chunks.length) {
        announce('Terminó el audio. Puedes escuchar otra vez o continuar.');
        return;
      }
      const utterance = new SpeechSynthesisUtterance(chunks[index++]);
      utterance.lang = selected?.lang || 'es-MX';
      utterance.rate = Number(voiceRate?.value || 0.92);
      utterance.pitch = 1.02;
      if (selected) utterance.voice = selected;
      utterance.onstart = () => announce('Reproduciendo audio. Puedes detenerlo cuando quieras.');
      utterance.onend = nextChunk;
      utterance.onerror = event => {
        if (thisReading === readingId && event.error !== 'canceled' && event.error !== 'interrupted')
          announce('No se pudo reproducir el audio. Prueba con otra voz o revisa el sonido.');
      };
      speech.speak(utterance);
    }
    nextChunk();
  }

  function pageText() {
    const main = document.querySelector('.page-content');
    if (!main) return document.body.innerText;
    const copy = main.cloneNode(true);
    copy.querySelectorAll('button, input, select, textarea, nav, script, style, .card-admin-actions, .activity-admin').forEach(el => el.remove());
    copy.querySelectorAll('[aria-hidden="true"]').forEach(el => el.remove());
    return copy.innerText || copy.textContent || '';
  }

  function setScale(value) {
    currentScale = Math.min(1.35, Math.max(0.9, Number(value.toFixed(2))));
    document.documentElement.style.zoom = String(currentScale);
    try { localStorage.setItem('alfamx-text-scale', String(currentScale)); } catch (_) { /* Preferencias opcionales. */ }
    announce(currentScale > 1 ? 'La pantalla está ampliada.' : currentScale < 1 ? 'La pantalla está reducida.' : 'Tamaño de pantalla normal.');
  }

  function setContrast(enabled) {
    document.body.dataset.highContrast = enabled ? 'true' : 'false';
    try { localStorage.setItem('alfamx-high-contrast', enabled ? 'true' : 'false'); } catch (_) { /* Preferencias opcionales. */ }
    const button = document.querySelector('[data-a11y-action="contrast"]');
    if (button) button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    announce(enabled ? 'Alto contraste activado.' : 'Alto contraste desactivado.');
  }

  function stopVoice() {
    readingId++;
    if (speech) speech.cancel();
    announce('Audio detenido.');
  }

  if (speech) {
    updateVoices();
    if (speech.addEventListener) speech.addEventListener('voiceschanged', updateVoices);
    else speech.onvoiceschanged = updateVoices;
  }
  if (voicePicker) voicePicker.addEventListener('change', () => {
    try { localStorage.setItem('alfamx-voice', voicePicker.value); } catch (_) { /* Preferencia opcional. */ }
    stopVoice();
    announce('Voz seleccionada. Pulsa Escuchar pantalla para probarla.');
  });
  if (voiceRate) {
    try { voiceRate.value = localStorage.getItem('alfamx-voice-rate') || '0.92'; } catch (_) { /* Preferencia opcional. */ }
    voiceRate.addEventListener('change', () => {
      try { localStorage.setItem('alfamx-voice-rate', voiceRate.value); } catch (_) { /* Preferencia opcional. */ }
      stopVoice();
      announce('Velocidad guardada. Pulsa Probar voz para escucharla.');
    });
  }

  document.addEventListener('click', event => {
    const speakButton = event.target.closest('[data-speak]');
    if (speakButton) {
      speak(speakButton.dataset.speak);
      return;
    }
    const actionButton = event.target.closest('[data-a11y-action]');
    if (!actionButton) return;
    switch (actionButton.dataset.a11yAction) {
      case 'read-page': speak(pageText()); break;
      case 'test-voice': speak('¡Hola! Soy tu acompañante de aprendizaje en Alfabetiza MX. Vamos a descubrir juntos el mundo de las palabras, a tu ritmo y paso a paso.'); break;
      case 'stop-voice': stopVoice(); break;
      case 'larger-text': setScale(currentScale + 0.1); break;
      case 'smaller-text': setScale(currentScale - 0.1); break;
      case 'contrast': setContrast(document.body.dataset.highContrast !== 'true'); break;
      default: break;
    }
  });

  // Restaura las preferencias de accesibilidad sin mostrar avisos de modo infantil/adulto.
  setScale(currentScale);
  let savedContrast = false;
  try { savedContrast = localStorage.getItem('alfamx-high-contrast') === 'true'; } catch (_) { /* Se usa contraste normal. */ }
  setContrast(savedContrast);
  window.AlfaMX = { speak, stopVoice };
})();
