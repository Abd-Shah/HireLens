import json
import os
import re
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

try:
    from groq import Groq
except Exception:
    Groq = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    import docx
except Exception:
    docx = None

load_dotenv()

st.set_page_config(
    page_title="HireLens AI JD Aligner",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #fff4f7;
    }
    [data-testid="stAppViewContainer"] {
        background: #fff4f7;
    }
    .main-title {font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem;}
    .subtle {color: #6b7280; font-size: 0.98rem;}
    .score-card {border: 1px solid #e5e7eb; border-radius: 18px; padding: 22px; background: #ffffff;}
    .score-card p {color: #111827;}
    .score-card div {color: #111827;}
    .suggestion-card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px; margin-bottom: 14px; background: #fafafa;}
    .good {color: #15803d; font-weight: 700;}
    .warn {color: #b45309; font-weight: 700;}
    .bad {color: #b91c1c; font-weight: 700;}
    .landing {
        min-height: 58vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        text-align: center;
    }
    .landing-title {
        font-size: clamp(3rem, 9vw, 7rem);
        font-weight: 900;
        color: #111827;
        margin-bottom: 1.5rem;
    }
    .landing-subtitle {
        color: #4b5563;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }
    .landing-button div[data-testid="stButton"] > button {
        background: #ff4f6d;
        border: 0;
        border-radius: 3px;
        color: #ffffff;
        font-weight: 700;
        height: 42px;
        min-height: 42px;
        padding: 0 28px;
    }
    .landing-button div[data-testid="stButton"] > button p {
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_text_from_pdf(uploaded_file) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed. Run: pip install pypdf")
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_text_from_docx(uploaded_file) -> str:
    if docx is None:
        raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    document = docx.Document(uploaded_file)
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()


def extract_text(uploaded_file) -> str:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore").strip()
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def extract_json_from_text(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("AI response did not contain valid JSON.")
        return json.loads(match.group(0))


def analyze_with_ai(resume_text: str, jd_text: str, model: str) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("No GROQ_API_KEY found. Add GROQ_API_KEY=gsk_your_key_here to your .env file.")
    if Groq is None:
        raise RuntimeError("groq is not installed. Run: pip install groq")

    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert ATS resume reviewer, technical recruiter, and resume editor for software engineering internships.

Analyze the resume against the job description using semantic understanding, not raw keyword matching.

Main goal:
Give a realistic alignment percentage and suggest targeted improvements that would make the resume more aligned with the JD.

Critical rules:
- Do NOT keyword stuff.
- Do NOT paste missing skills into every bullet.
- Do NOT list random common words as matches or missing skills.
- Only treat real technologies, tools, frameworks, responsibilities, qualifications, domain knowledge, documents, eligibility items, and role requirements as relevant.
- Do NOT invent experience.
- Do NOT claim the candidate has tools, languages, or frameworks unless the resume supports them.
- If a missing JD skill is not present in the resume, recommend adding it only if the candidate genuinely has that experience.
- Rewrite bullets only when the improvement is natural, truthful, and tied to the original bullet.
- Suggested bullet rewrites must sound like real resume bullets written by a human.
- Do NOT generate vague rewrites.
- Do NOT add unnecessary filler words or generic buzzwords.
- Do NOT use semicolons at the end of bullets.
- Preserve all original metrics when rewriting bullets.
- Keep suggested bullets concise, technical, ATS-friendly, and directly usable in a real resume.
- Each rewritten bullet should clearly improve alignment with a specific JD requirement.
- The explanation for each suggestion must specifically explain what JD requirement the rewrite improves.
- Only suggest 3 to 5 high-impact resume improvements.
- Prefer clarity, technical accuracy, and ATS relevance over buzzwords.
- Keep suggested bullets concise and resume-ready.
- Identify required documents, eligibility items, GPA/transcript requirements, relocation/location, work authorization, language requirements, or schedule requirements mentioned in the JD.
- The alignment score should reflect technical fit, role responsibility fit, domain fit, eligibility fit, and missing required skills.

Return only valid JSON in this exact shape:
{{
  "alignment_score": 0,
  "summary": "",
  "strong_matches": [""],
  "missing_or_weak_matches": [
    {{
      "requirement": "",
      "status": "missing | weak | partial",
      "recommendation": ""
    }}
  ],
  "overall_recommendations": [""],
  "suggested_bullet_improvements": [
    {{
      "section": "Work Experience | Projects | Summary | Skills",
      "original": "",
      "suggested": "",
      "reason": ""
    }}
  ],
  "document_requirements": [""],
  "truthfulness_notes": [""]
}}

Job Description:
{jd_text}

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You produce truthful, structured resume-to-JD alignment analysis in valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    return extract_json_from_text(content)


def score_label(score: int) -> str:
    if score >= 85:
        return "Strong match"
    if score >= 70:
        return "Good match"
    if score >= 55:
        return "Moderate match"
    return "Needs major tailoring"


def score_class(score: int) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "warn"
    return "bad"


if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown(
        """
        <div class="landing">
            <div class="landing-title">HireLens</div>
            <div class="landing-subtitle">Match your resume to the job before you apply.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, button_col, _ = st.columns([2.25, 0.5, 2.25])
    with button_col:
        st.markdown('<div class="landing-button">', unsafe_allow_html=True)
        if st.button("Get Started", type="primary", use_container_width=True):
            st.session_state.started = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


st.markdown('<div class="main-title">HireLens AI JD Aligner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtle">Upload a resume, paste a job description, and get an AI-powered alignment score with realistic improvement suggestions. No keyword stuffing.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Groq model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0,
    )
    st.caption("Requires GROQ_API_KEY in your .env file. No keyword fallback is used.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Resume")
    uploaded_resume = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    resume_text_manual = st.text_area("Or paste resume text", height=280, placeholder="Paste resume text here...")

with col2:
    st.subheader("2. Job Description")
    jd_text = st.text_area("Paste JD", height=350, placeholder="Paste the full job description here...")

run_analysis = st.button("Analyze Resume Alignment", type="primary", use_container_width=True)

if run_analysis:
    try:
        resume_text = resume_text_manual.strip()
        if uploaded_resume is not None:
            resume_text = extract_text(uploaded_resume)

        if not resume_text:
            st.error("Please upload or paste a resume.")
            st.stop()
        if not jd_text.strip():
            st.error("Please paste a job description.")
            st.stop()

        with st.spinner("Comparing resume against the JD..."):
            result = analyze_with_ai(resume_text, jd_text.strip(), model)

        score = int(result.get("alignment_score", 0))
        label = score_label(score)
        css_class = score_class(score)

        st.markdown("---")
        st.markdown("### Alignment Result")
        st.markdown(
            f"""
            <div class="score-card">
                <div style="font-size: 3rem; font-weight: 900;" class="{css_class}">{score}%</div>
                <div style="font-size: 1.2rem; font-weight: 700;">{label}</div>
                <p>{result.get('summary', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Strong Matches")
            strong_matches = result.get("strong_matches", []) or []
            if strong_matches:
                for item in strong_matches:
                    st.success(str(item))
            else:
                st.info("No strong matches returned.")

        with c2:
            st.markdown("### Missing or Weak Matches")
            weak_matches = result.get("missing_or_weak_matches", []) or []
            if weak_matches:
                for item in weak_matches:
                    requirement = item.get("requirement", "Requirement")
                    status = item.get("status", "weak")
                    recommendation = item.get("recommendation", "")
                    st.warning(f"**{requirement}** ({status}): {recommendation}")
            else:
                st.info("No major weak areas returned.")

        overall_recommendations = result.get("overall_recommendations", []) or []
        if overall_recommendations:
            st.markdown("### Overall Resume Recommendations")
            for rec in overall_recommendations:
                st.info(str(rec))

        st.markdown("### Targeted Resume Improvements")
        suggestions = result.get("suggested_bullet_improvements", []) or []
        if suggestions:
            for idx, suggestion in enumerate(suggestions, start=1):
                with st.expander(f"Suggestion {idx}: {suggestion.get('section', 'Resume')}", expanded=True):
                    st.markdown("**Original**")
                    st.write(suggestion.get("original", ""))
                    st.markdown("**Suggested Improvement**")
                    st.success(suggestion.get("suggested", ""))
                    st.markdown("**Why this improves JD alignment**")
                    st.write(suggestion.get("reason", ""))
        else:
            st.info("No bullet rewrites were suggested. The AI may have found the current bullets already appropriate or insufficient evidence to rewrite truthfully.")

        doc_requirements = result.get("document_requirements", []) or []
        if doc_requirements:
            st.markdown("### Application / Document Requirements Found in JD")
            for item in doc_requirements:
                st.info(str(item))

        truth_notes = result.get("truthfulness_notes", []) or []
        if truth_notes:
            st.markdown("### Truthfulness Notes")
            for note in truth_notes:
                st.caption(f"• {note}")

        with st.expander("Raw JSON output"):
            st.json(result)

    except Exception as exc:
        st.error(f"Something went wrong: {exc}")
