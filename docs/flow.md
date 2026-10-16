# Interview flow

```mermaid
flowchart TD
  A[Prepare] --> B[Upload or paste resume]
  B --> C[Extract and edit resume text]
  C --> D[Choose target role and optional job description]
  D --> E[Ollama creates five interview questions]
  E --> F[Ask question]
  F --> G{Answer method}
  G -->|Microphone| H[faster-whisper transcription]
  G -->|Typed| I[Use edited answer text]
  H --> I
  I --> J[Candidate reviews and submits]
  J --> K[Ollama evaluates relevance, clarity, evidence]
  K --> L{Needs more evidence?}
  L -->|Yes| M[Ask focused follow-up]
  M --> F
  L -->|No| N{More questions?}
  N -->|Yes| F
  N -->|No| O[Generate structured report]
  O --> P[Review and edit report]
  P --> Q{Candidate approves export?}
  Q -->|No| P
  Q -->|Yes| R[Download Markdown]
```

## Report fields

- Overall summary and role context
- Relevance, clarity, and evidence ratings from 1 to 5
- Specific strengths and improvement suggestions
- Notes tied to each submitted answer

The report explicitly describes the scores as practice guidance. It is intended to help a candidate reflect on their answers, not rank or screen job applicants.
