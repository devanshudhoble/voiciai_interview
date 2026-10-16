from __future__ import annotations

from functools import lru_cache
from io import BytesIO


@lru_cache(maxsize=1)
def _model():
    from faster_whisper import WhisperModel

    return WhisperModel("base.en", device="cpu", compute_type="int8")


def transcribe_audio(wav_bytes: bytes) -> str:
    segments, _ = _model().transcribe(BytesIO(wav_bytes), language="en", beam_size=3, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()
