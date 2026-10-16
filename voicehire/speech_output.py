from __future__ import annotations

import json


def speech_button(text: str) -> str:
    """Render a browser speech button restricted to voices installed locally."""
    encoded_text = json.dumps(text, ensure_ascii=True).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, 'Segoe UI', sans-serif; color: #17201f; }}
    button {{ border: 1px solid #d7e1dd; border-radius: 10px; padding: 10px 14px;
      background: #fff; color: #173a35; font: 600 14px Inter, 'Segoe UI', sans-serif;
      cursor: pointer; }}
    button:hover {{ background: #e9f4ef; border-color: #0d766e; }}
    button:focus-visible {{ outline: 3px solid #0d766e; outline-offset: 2px; }}
    #status {{ margin-left: 10px; color: #586662; font-size: 12px; }}
  </style>
</head>
<body>
  <button id="speak" type="button">🔊 Hear this question</button>
  <span id="status" role="status" aria-live="polite"></span>
  <script>
    const questionText = {encoded_text};
    const status = document.getElementById('status');
    document.getElementById('speak').addEventListener('click', () => {{
      if (!('speechSynthesis' in window)) {{
        status.textContent = 'Speech playback is not supported by this browser.';
        return;
      }}
      const voices = window.speechSynthesis.getVoices();
      const localVoices = voices.filter((voice) => voice.localService);
      if (!localVoices.length) {{
        status.textContent = 'Install a local system voice to hear questions.';
        return;
      }}
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(questionText);
      utterance.voice = localVoices.find((voice) => voice.lang.toLowerCase().startsWith('en')) || localVoices[0];
      utterance.rate = 0.96;
      utterance.onstart = () => {{ status.textContent = 'Speaking…'; }};
      utterance.onend = () => {{ status.textContent = ''; }};
      utterance.onerror = () => {{ status.textContent = 'Could not play the local voice.'; }};
      window.speechSynthesis.speak(utterance);
    }});
  </script>
</body>
</html>"""
