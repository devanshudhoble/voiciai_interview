from __future__ import annotations

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    prompt: str = Field(min_length=8)
    category: str = "Behavioral"
    difficulty: str = "Medium"
    intent: str = ""


class Improvement(BaseModel):
    title: str
    detail: str
    example: str = ""


class AnswerNote(BaseModel):
    question: str
    note: str


class AnswerEvaluation(BaseModel):
    relevance: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    evidence: int = Field(ge=1, le=5)
    summary: str
    follow_up: str | None = None


class FeedbackReport(BaseModel):
    role_context: str
    overall_summary: str
    relevance: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    evidence: int = Field(ge=1, le=5)
    strengths: list[str]
    improvements: list[Improvement]
    answer_notes: list[AnswerNote]

    def to_markdown(self) -> str:
        lines = [
            "# VoiceHire interview feedback",
            f"\n**Role:** {self.role_context}",
            f"\n{self.overall_summary}",
            "\n## Summary scores",
            f"- Relevance: {self.relevance}/5",
            f"- Clarity: {self.clarity}/5",
            f"- Evidence: {self.evidence}/5",
            "\n## Strengths",
            *(f"- {item}" for item in self.strengths),
            "\n## Opportunities to improve",
        ]
        for item in self.improvements:
            lines.append(f"- **{item.title}:** {item.detail}")
            if item.example:
                lines.append(f"  - Try: {item.example}")
        lines.append("\n## Answer notes")
        for item in self.answer_notes:
            lines.extend([f"\n### {item.question}", item.note])
        lines.append("\n---\nGenerated locally by VoiceHire. Use this feedback as practice guidance, not as a hiring decision.")
        return "\n".join(lines)
