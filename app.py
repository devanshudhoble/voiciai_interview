from __future__ import annotations

import os
from html import escape
from typing import Any

import streamlit as st
from streamlit.components.v1 import html as component_html

from voicehire.interviewer import Interviewer
from voicehire.resume_parser import extract_resume_text
from voicehire.schemas import FeedbackReport, InterviewQuestion
from voicehire.speech_output import speech_button
from voicehire.transcription import transcribe_audio

st.set_page_config(page_title="VoiceHire | Interview practice", page_icon="🎙️", layout="wide")
st.markdown("""
<style>
:root { --ink:#17201f; --muted:#6d7976; --teal:#0d766e; --paper:#f5f7f4; }
.stApp { background:var(--paper); color:var(--ink); font-family:Inter,'Segoe UI',sans-serif; overflow-x:clip; }
[data-testid="stHeader"] { background:transparent; }
.block-container { box-sizing:border-box; width:calc(100% - 1rem); padding:2rem 1.5rem; max-width:1240px; min-width:0; }
[data-testid="stAppViewContainer"], section.main, .stMainBlockContainer { box-sizing:border-box; max-width:100%; min-width:0; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; }
h1 { font-size:2.45rem !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p { color:#44514e !important; }
[data-testid="stSidebar"] { background:#102a27; }
[data-testid="stSidebar"] * { color:#e6f2ee !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#b8ccc7 !important; }
.eyebrow { color:var(--teal); text-transform:uppercase; letter-spacing:.15em; font-size:.73rem; font-weight:700; }
.hero { background:linear-gradient(120deg,#103c36,#17685f); color:white; padding:1.8rem 2rem; border-radius:22px; margin:.5rem 0 1.4rem; }
.hero h1 { color:white; margin:.3rem 0 .45rem; }
.hero p { color:#d0e5df; max-width:700px; font-size:1.02rem; }
.hero .eyebrow { color:#a8e1ce; }
.question-card { box-sizing:border-box; width:100%; max-width:100%; min-width:0; overflow-wrap:anywhere; background:white; border-left:5px solid #0d766e; border-radius:14px; padding:1.1rem 1.35rem; margin:.8rem 0 1.2rem; box-shadow:0 8px 28px rgba(20,45,39,.05); }
.question-card h3 { max-width:100%; min-width:0; white-space:normal; overflow-wrap:anywhere; word-break:normal; }
.metric-card { background:white; border:1px solid #e5ebe7; padding:1rem; border-radius:15px; min-height:95px; }
.muted { color:var(--muted); }
div.stButton > button[kind="primary"] { background:#0d766e; border-color:#0d766e; border-radius:10px; font-weight:700; }
div.stButton > button { border-radius:10px; }
[data-testid="stForm"] { background:#fff; border:1px solid #e5ebe7; border-radius:15px; padding:1.1rem; }
hr { border-color:#e0e8e4; }
@media (max-width:640px) {
  .block-container { padding:1.25rem .9rem 2rem; }
  h1 { font-size:1.9rem !important; }
  .question-card { padding:1rem; }
}
</style>
""", unsafe_allow_html=True)


def init_state() -> None:
    defaults: dict[str, Any] = {
        "resume_text": "", "resume_name": "", "role": "", "job_description": "",
        "questions": [], "answers": [], "active_question": 0, "report": None, "approved": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_interview() -> None:
    for key, value in {"questions": [], "answers": [], "active_question": 0, "report": None, "approved": False}.items():
        st.session_state[key] = value


def sidebar() -> str:
    with st.sidebar:
        st.markdown("## 🎙️ VoiceHire")
        st.caption("A private, local-first interview coach")
        st.divider()
        step = st.radio("WORKSPACE", ["1 · Prepare", "2 · Interview", "3 · Feedback"])
        st.divider()
        st.markdown("**Your setup**")
        st.caption(f"Role · {st.session_state.role or 'Not selected'}")
        st.caption(f"Resume · {st.session_state.resume_name or 'Not uploaded'}")
        st.caption(f"Model · {os.getenv('OLLAMA_MODEL', 'llama3.2:latest')}")
        if st.button("Start a fresh interview", use_container_width=True):
            reset_interview()
            st.rerun()
        st.divider()
        st.caption("Runs on this computer. Your resume stays in this session unless you export it.")
    return step


def render_prepare(interviewer: Interviewer) -> None:
    st.markdown('<div class="eyebrow">01 / Personalise your session</div>', unsafe_allow_html=True)
    st.title("Prepare your interview")
    st.write("Add your resume and target role. VoiceHire will tailor practice questions to your experience.")
    left, right = st.columns([1.08, .92], gap="large")
    with left:
        st.markdown("### Your background")
        uploaded = st.file_uploader("Upload a resume", type=["pdf", "docx", "txt"], help="PDF, Word, or plain text · up to 10 MB")
        if uploaded:
            if uploaded.size > 10 * 1024 * 1024:
                st.error("Please use a resume smaller than 10 MB.")
            else:
                try:
                    extracted = extract_resume_text(uploaded.name, uploaded.getvalue())
                    if not extracted.strip():
                        st.error("No readable text found. Try a text-based PDF or paste your resume below.")
                    else:
                        st.session_state.resume_text = extracted[:24000]
                        st.session_state.resume_name = uploaded.name
                        st.success(f"Resume ready · {len(extracted.split())} words extracted")
                except Exception as exc:
                    st.error(f"Could not read this file: {exc}")
        st.text_area("Resume text (edit extracted text if needed)", height=220, placeholder="Upload a resume or paste relevant experience here…", key="resume_text")
    with right:
        st.markdown("### The role")
        st.text_input("Target job title", placeholder="e.g. Junior Product Designer", key="role")
        st.text_area("Job description (optional)", height=160, placeholder="Paste the role requirements to tailor your practice…", key="job_description")
        st.markdown("### Session format")
        st.info("5 questions · voice or typed answers · reviewable feedback", icon="🧭")
        status = interviewer.status()
        if status:
            st.success(status)
        else:
            st.warning(f"Ollama is not ready at {interviewer.base_url}. Start Ollama and pull the configured model. See the README for setup.", icon="🖥️")
        if st.button("Build my interview →", type="primary", use_container_width=True, disabled=not st.session_state.role.strip()):
            if not st.session_state.resume_text.strip():
                st.warning("Add resume text or upload a resume to continue.")
            else:
                try:
                    with st.spinner("Creating your role-specific interview…"):
                        questions = interviewer.create_questions(st.session_state.role, st.session_state.job_description, st.session_state.resume_text)
                    st.session_state.questions = [item.model_dump() for item in questions]
                    st.session_state.answers = []
                    st.session_state.active_question = 0
                    st.session_state.report = None
                    st.session_state.approved = False
                    st.success("Your interview is ready. Choose Interview in the left menu.")
                except Exception as exc:
                    st.error(f"Could not create questions: {exc}")


def render_interview(interviewer: Interviewer) -> None:
    st.markdown('<div class="eyebrow">02 / Practice</div>', unsafe_allow_html=True)
    st.title("Your interview room")
    questions = st.session_state.questions
    if not questions:
        st.info("Prepare a session first to see your first question.")
        return
    idx = st.session_state.active_question
    total = len(questions)
    if idx >= total:
        st.success("Interview complete. Open Feedback to build your report.")
        return
    question = InterviewQuestion.model_validate(questions[idx])
    st.progress(idx / total, text=f"Question {idx + 1} of {total}")
    st.markdown(f'<div class="question-card"><div class="eyebrow">{escape(question.category)} · {escape(question.difficulty)}</div><h3>{escape(question.prompt)}</h3><div class="muted">{escape(question.intent)}</div></div>', unsafe_allow_html=True)
    component_html(speech_button(question.prompt), height=58, scrolling=False)
    st.caption("Listen, record your answer or type one below. Review the transcript before submitting.")
    voice = st.audio_input("Record your answer", sample_rate=16000, key=f"voice_{idx}")
    if voice and st.button("Transcribe recording", key=f"transcribe_{idx}"):
        try:
            with st.spinner("Transcribing locally… the first run downloads the speech model."):
                transcript = transcribe_audio(voice.getvalue())
                st.session_state[f"transcript_{idx}"] = transcript
                st.session_state[f"answer_{idx}"] = transcript
            st.rerun()
        except Exception as exc:
            st.error(f"Transcription failed: {exc}")
    st.text_area("Your answer", height=180, placeholder="Tell your story. A useful structure is Situation, Task, Action, Result.", key=f"answer_{idx}")
    answer = st.session_state.get(f"answer_{idx}", "")
    if st.button("Submit answer →", type="primary", disabled=not answer.strip()):
        try:
            with st.spinner("Reviewing your answer…"):
                feedback = interviewer.evaluate_answer(question, answer, st.session_state.role)
            st.session_state.answers.append({"question": question.model_dump(), "answer": answer.strip(), "feedback": feedback})
            follow_up = feedback.get("follow_up")
            if follow_up and len(st.session_state.answers) <= 5:
                questions.insert(idx + 1, {"prompt": follow_up, "category": "Follow-up", "difficulty": "Medium", "intent": "Clarify the evidence in your previous answer."})
                st.session_state.questions = questions
            st.session_state.active_question += 1
            st.rerun()
        except Exception as exc:
            st.error(f"Could not process this answer: {exc}")
    if st.session_state.answers:
        with st.expander(f"Review previous answers ({len(st.session_state.answers)})"):
            for item in st.session_state.answers:
                st.markdown(f"**{item['question']['prompt']}**")
                st.write(item["answer"])
                st.caption(item["feedback"].get("summary", ""))


def render_feedback(interviewer: Interviewer) -> None:
    st.markdown('<div class="eyebrow">03 / Reflect and improve</div>', unsafe_allow_html=True)
    st.title("Your feedback report")
    answers = st.session_state.answers
    if not answers:
        st.info("Complete at least one interview answer to create a report.")
        return
    if len(answers) < len(st.session_state.questions):
        st.caption(f"You have answered {len(answers)} of {len(st.session_state.questions)} questions. Create a progress report now or continue the interview.")
    if st.session_state.report is None and st.button("Generate feedback report", type="primary"):
        try:
            with st.spinner("Building your report from the interview transcript…"):
                st.session_state.report = interviewer.create_report(st.session_state.role, answers).model_dump()
                st.session_state.approved = False
        except Exception as exc:
            st.error(f"Could not generate report: {exc}")
    if st.session_state.report is None:
        return
    report = FeedbackReport.model_validate(st.session_state.report)
    st.markdown(f"### {report.overall_summary}")
    st.caption(report.role_context)
    cols = st.columns(3)
    for col, (label, score) in zip(cols, [("Relevance", report.relevance), ("Clarity", report.clarity), ("Evidence", report.evidence)]):
        with col:
            st.markdown(f'<div class="metric-card"><span class="muted">{label}</span><h2>{score}/5</h2></div>', unsafe_allow_html=True)
    st.markdown("### What you did well")
    for strength in report.strengths:
        st.markdown(f"- {strength}")
    st.markdown("### Opportunities to improve")
    for item in report.improvements:
        st.markdown(f"- **{item.title}:** {item.detail}")
        if item.example:
            st.caption(f"Try: {item.example}")
    st.markdown("### Answer-by-answer notes")
    for item in report.answer_notes:
        with st.expander(item.question):
            st.write(item.note)
    st.divider()
    st.markdown("### Review and approve")
    edited = st.text_area("Edit the report before export (Markdown)", value=report.to_markdown(), height=300)
    st.session_state.approved = st.checkbox("I reviewed this report and approve exporting it.", value=st.session_state.approved)
    if st.session_state.approved:
        st.download_button("Download approved report", data=edited, file_name="voicehire-interview-feedback.md", mime="text/markdown", type="primary")
    else:
        st.caption("Review and approve the report to enable download.")


def main() -> None:
    init_state()
    step = sidebar()
    interviewer = Interviewer(os.getenv("OLLAMA_HOST", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:latest"))
    st.markdown('<div class="hero"><div class="eyebrow">Your private interview practice studio</div><h1>Show up ready.</h1><p>Practice with a role-aware interviewer, answer in your own words, and leave with a clear plan to improve.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, label, value in [(c1, "TARGET ROLE", st.session_state.role or "Not set"), (c2, "ANSWERS PRACTISED", f"{len(st.session_state.answers)} recorded"), (c3, "SESSION", "Local & private")]:
        with col:
            st.markdown(f'<div class="metric-card"><span class="muted">{label}</span><h3>{value}</h3></div>', unsafe_allow_html=True)
    st.write("")
    if step.startswith("1"):
        render_prepare(interviewer)
    elif step.startswith("2"):
        render_interview(interviewer)
    else:
        render_feedback(interviewer)


if __name__ == "__main__":
    main()
