# Architecture

## Design goals

- Keep resume parsing, speech recognition, model calls, validation, and presentation in separate modules.
- Default all model inference to local processes; no hosted AI key is required.
- Validate model output at service boundaries before showing or exporting it.
- Require user review and approval before report download.
- Keep session answers in memory for this MVP; avoid storing sensitive resume data by default.

## Components

| Component | Responsibility | Boundary |
| --- | --- | --- |
| `app.py` | Streamlit screens, session state, interaction and approval | UI calls typed service methods |
| `resume_parser.py` | Extract plain text from PDF, DOCX and TXT | Receives bytes; returns text |
| `transcription.py` | Lazy-load faster-whisper and transcribe WAV input | Receives audio bytes; returns transcript |
| `speech_output.py` | Use installed operating system voice to speak a question | Receives text; returns temporary WAV bytes |
| `interviewer.py` | Call local Ollama for questions, evaluations and report | HTTP JSON + Pydantic validation |
| `schemas.py` | Define question/evaluation/report contracts | Validates response and renders Markdown |

## Data flow

1. User uploads a resume. Parser extracts text, which is held in the current Streamlit session and can be edited.
2. Interview service sends role, job description, and resume context to Ollama. Five question objects are constrained to a JSON schema and validated. Optional playback uses the computer's installed speech voice.
3. For each answer, audio is transcribed locally (or text is used directly). Ollama returns three rubric scores, a short note, and an optional follow-up question.
4. The report service receives the transcript and initial answer notes. It returns a validated report with strengths, improvements, and answer-by-answer notes.
5. User can edit the report as Markdown. Download stays disabled until the approval checkbox is selected.

## Local model interface

VoiceHire calls Ollama's local `/api/tags` and `/api/chat` endpoints. `OLLAMA_HOST` and `OLLAMA_MODEL` can be set in the process environment. The default endpoint is `http://localhost:11434`, and the default model is `qwen3.5:4b`.

## Current limits

- Scanned PDF OCR is not included.
- Speech output quality depends on the system voice installed on the computer.
- Session history and authentication are not included; state is ephemeral.
- Model scores are subjective practice feedback and can vary between runs.
- Large resume text and job descriptions are truncated or should be kept concise for small local models.
