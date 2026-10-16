from __future__ import annotations

import os
import tempfile


def speak(text: str) -> bytes:
    """Create question audio using the operating system's installed voice."""
    import pyttsx3

    handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    path = handle.name
    handle.close()
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, path)
        engine.runAndWait()
        with open(path, "rb") as audio_file:
            return audio_file.read()
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
