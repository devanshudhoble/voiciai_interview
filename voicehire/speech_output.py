from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


VOICE_NAME = os.getenv("VOICEHIRE_PIPER_VOICE", "en_US-lessac-medium")
VOICE_DIR = Path(__file__).resolve().parents[1] / "data" / "voices"


def _voice_model_path() -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", VOICE_NAME):
        raise ValueError("VOICEHIRE_PIPER_VOICE contains unsupported characters.")
    model_path = VOICE_DIR / f"{VOICE_NAME}.onnx"
    config_path = VOICE_DIR / f"{VOICE_NAME}.onnx.json"
    if model_path.is_file() and config_path.is_file():
        return model_path

    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "piper.download_voices", VOICE_NAME, "--download-dir", str(VOICE_DIR)],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(f"Could not download the local Piper voice: {details[-1000:]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("The voice download timed out. Check your internet connection and try again.") from exc
    if not model_path.is_file() or not config_path.is_file():
        raise RuntimeError("Piper finished without creating both voice files. Please try again.")
    return model_path


def speak(text: str) -> bytes:
    """Synthesize question audio with Piper's local command-line voice engine."""
    model_path = _voice_model_path()
    with tempfile.TemporaryDirectory(prefix="voicehire-") as temp_dir:
        wav_path = Path(temp_dir) / "question.wav"
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "piper",
                    "--model",
                    str(model_path),
                    "--output-file",
                    str(wav_path),
                    "--",
                    text,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Local speech synthesis timed out. Try again or use a shorter question.") from exc
        if result.returncode != 0:
            details = (result.stderr or result.stdout or "Piper returned an error.").strip()
            raise RuntimeError(details[-1000:])
        if not wav_path.is_file():
            raise RuntimeError("Piper did not produce the question audio file.")
        return wav_path.read_bytes()
