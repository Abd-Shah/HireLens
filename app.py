import base64
import json
import os
import re
from pathlib import Path
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

hero_bg_path = Path(__file__).parent / "assets" / "hero-background.png"
hero_bg_data = ""
if hero_bg_path.exists():
    hero_bg_data = base64.b64encode(hero_bg_path.read_bytes()).decode("utf-8")

st.set_page_config(
    page_title="HireLens AI JD Aligner",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #061a32;
    }
    [data-testid="stAppViewContainer"] {
        background: #061a32;
    }
    [data-testid="stHeader"] {
        display: none;
    }
    .block-container {
        max-width: 100%;
        padding: 0;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        padding-top: 0;
        text-align: center;
    }
    .subtle {
        color: #6b7280;
        font-size: 0.98rem;
        text-align: center;
    }
    .analyzer-spacer {
        height: 3.25rem;
    }
    .analyzer-page {
        animation: pageEnter 0.55s ease-out both;
    }
    .analyzer-back {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 36px;
        padding: 0 1rem;
        border-radius: 999px;
        color: rgba(255, 255, 255, 0.86) !important;
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(255, 255, 255, 0.06);
        text-decoration: none;
        font-size: 0.82rem;
        font-weight: 800;
        transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
    }
    .analyzer-back:hover {
        background: #ffffff;
        color: #0b3d75 !important;
        border-color: #ffffff;
        text-decoration: none;
    }
    .score-card {border: 1px solid #e5e7eb; border-radius: 18px; padding: 22px; background: #ffffff;}
    .score-card p {color: #111827;}
    .score-card div {color: #111827;}
    .suggestion-card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px; margin-bottom: 14px; background: #fafafa;}
    .good {color: #15803d; font-weight: 700;}
    .warn {color: #b45309; font-weight: 700;}
    .bad {color: #b91c1c; font-weight: 700;}
    .hero-shell {
        min-height: 100vh;
        width: 100%;
        border-radius: 0;
        overflow: hidden;
        color: #ffffff;
        background:
            linear-gradient(90deg, rgba(4, 39, 83, 0.82) 0%, rgba(12, 74, 123, 0.62) 44%, rgba(7, 42, 83, 0.28) 100%),
            url("data:image/png;base64,__HERO_BG__");
        background-size: cover;
        background-position: center;
        box-shadow: none;
        position: relative;
        animation: pageEnter 0.55s ease-out both;
    }
    .hero-nav {
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4.75rem;
        font-size: 0.78rem;
        font-weight: 700;
        background: rgba(3, 34, 70, 0.92);
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.12);
    }
    .hero-links {
        display: flex;
        align-items: center;
        gap: 2.35rem;
        color: rgba(255, 255, 255, 0.88);
    }
    .hero-nav-cta {
        background: transparent;
        color: #4aa8ff !important;
        border-radius: 999px;
        padding: 0.58rem 1.2rem;
        text-decoration: none;
        opacity: 1;
        transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
    }
    .hero-link {
        color: #4aa8ff !important;
        text-decoration: none;
        border-radius: 999px;
        padding: 0.58rem 1rem;
        transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
    }
    .hero-link:visited,
    .hero-link:active,
    .hero-nav-cta:visited,
    .hero-nav-cta:active {
        color: #4aa8ff !important;
        text-decoration: none;
    }
    .hero-link:hover,
    .hero-nav-cta:hover {
        background: #ffffff;
        color: #0b3d75 !important;
        box-shadow: 0 10px 24px rgba(255, 255, 255, 0.18);
        text-decoration: none;
    }
    .hero-content {
        min-height: calc(100vh - 5rem);
        display: grid;
        grid-template-columns: minmax(0, 1fr) 560px;
        align-items: center;
        gap: 5rem;
        padding: 1rem 8rem 6.5rem 8rem;
    }
    .hero-copy {
        max-width: 620px;
    }
    .hero-eyebrow {
        color: rgba(255, 255, 255, 0.82);
        font-size: 0.8rem;
        font-weight: 800;
        margin-bottom: 1.25rem;
    }
    .landing-title {
        font-size: clamp(4rem, 9vw, 7.25rem);
        line-height: 0.9;
        font-weight: 900;
        color: #ffffff;
        margin: 0 0 1.5rem 0;
        animation: slideTitleIn 1.2s ease-out forwards;
    }
    .landing-subtitle {
        color: rgba(255, 255, 255, 0.86);
        font-size: 1rem;
        line-height: 1.65;
        max-width: 470px;
        margin-bottom: 2rem;
        animation: fadeIn 0.7s ease-out 1.1s both;
    }
    .hero-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: fadeInUp 0.55s ease-out 1.2s both;
    }
    .hero-primary,
    .hero-secondary {
        height: 42px;
        padding: 0 1.35rem;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.85rem;
        text-decoration: none;
        opacity: 1;
        -webkit-font-smoothing: antialiased;
        text-rendering: geometricPrecision;
    }
    .hero-primary {
        background: #1d5cff;
        color: #ffffff !important;
        box-shadow: 0 12px 30px rgba(29, 92, 255, 0.35);
    }
    .hero-secondary {
        border: 1px solid rgba(255, 255, 255, 0.7);
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.12);
    }
    .hero-primary:visited,
    .hero-primary:hover,
    .hero-primary:active,
    .hero-secondary:visited,
    .hero-secondary:hover,
    .hero-secondary:active {
        color: #ffffff !important;
        text-decoration: none;
    }
    .score-float {
        width: 560px;
        min-height: 430px;
        align-self: center;
        justify-self: start;
        position: relative;
        transform: translate(-30px, 60px);
        animation: fadeInUp 0.7s ease-out 1.1s both;
    }
    .hero-insight-card {
        position: absolute;
        border-radius: 18px;
        padding: 1.25rem;
        color: #ffffff;
        background: rgba(35, 90, 139, 0.62);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.24);
        backdrop-filter: blur(16px);
    }
    .hero-insight-card.primary {
        width: 275px;
        min-height: 260px;
        top: -45px;
        left: 142px;
        z-index: 3;
    }
    .hero-insight-card.top {
        width: 210px;
        min-height: 125px;
        top: 285px;
        left: -8px;
        z-index: 2;
    }
    .hero-insight-card.bottom {
        width: 235px;
        min-height: 142px;
        right: 0;
        top: 290px;
        z-index: 4;
    }
    .card-kicker {
        color: rgba(255, 255, 255, 0.78);
        font-size: 0.76rem;
        font-weight: 900;
        margin-bottom: 0.55rem;
    }
    .card-title {
        color: #ffffff;
        font-size: 1.05rem;
        line-height: 1.25;
        font-weight: 900;
        margin-bottom: 0.8rem;
    }
    .card-copy {
        color: rgba(255, 255, 255, 0.76);
        font-size: 0.82rem;
        line-height: 1.5;
    }
    .score-ring {
        width: 142px;
        height: 142px;
        border-radius: 999px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0.65rem auto 1rem auto;
        background:
            radial-gradient(circle at center, rgba(14, 44, 83, 0.96) 0 54%, transparent 55%),
            conic-gradient(#87f2ce 0 320deg, rgba(255, 255, 255, 0.16) 320deg 360deg);
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
    }
    .score-ring-number {
        font-size: 2.55rem;
        line-height: 1;
        font-weight: 900;
        color: #ffffff;
    }
    .score-ring-label {
        color: rgba(255, 255, 255, 0.78);
        font-size: 0.72rem;
        font-weight: 800;
        margin-top: 0.28rem;
    }
    .suggestion-bars {
        display: grid;
        gap: 0.55rem;
        margin-top: 0.2rem;
    }
    .suggestion-bar {
        height: 7px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.25);
    }
    .suggestion-bar.accent {
        width: 78%;
        background: #87f2ce;
    }
    .suggestion-bar.mid {
        width: 62%;
    }
    .metric-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.8rem;
        margin-top: 1rem;
    }
    .metric-value {
        color: #87f2ce;
        font-size: 1.75rem;
        line-height: 1;
        font-weight: 900;
    }
    .metric-label {
        color: rgba(255, 255, 255, 0.76);
        font-size: 0.75rem;
        font-weight: 800;
    }
    .how-shell {
        min-height: 100vh;
        color: #ffffff;
        background:
            linear-gradient(135deg, rgba(4, 22, 45, 0.94) 0%, rgba(13, 72, 124, 0.88) 52%, rgba(3, 22, 45, 0.92) 100%),
            url("data:image/png;base64,__HERO_BG__");
        background-size: cover;
        background-position: center;
        animation: pageEnter 0.55s ease-out both;
    }
    .how-nav {
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4.75rem;
        font-size: 0.82rem;
        font-weight: 800;
    }
    .how-back {
        color: #ffffff;
        text-decoration: none;
        border: 1px solid rgba(255, 255, 255, 0.45);
        border-radius: 999px;
        padding: 0.65rem 1rem;
        background: rgba(255, 255, 255, 0.08);
    }
    .how-back:visited,
    .how-back:hover,
    .how-back:active {
        color: #ffffff;
        text-decoration: none;
    }
    .how-content {
        max-width: 1120px;
        margin: 0 auto;
        padding: 7rem 2rem 5rem 2rem;
    }
    .how-kicker {
        color: #87f2ce;
        font-size: 0.82rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    .how-title {
        font-size: clamp(3rem, 7vw, 6.5rem);
        line-height: 0.95;
        font-weight: 900;
        max-width: 820px;
        margin: 0 0 1.35rem 0;
    }
    .how-intro {
        color: rgba(255, 255, 255, 0.82);
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 670px;
        margin-bottom: 3rem;
    }
    .how-steps {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.2rem;
    }
    .how-step {
        min-height: 230px;
        border-radius: 16px;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.2);
    }
    .how-number {
        width: 40px;
        height: 40px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1d5cff;
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 1.3rem;
    }
    .how-step h3 {
        color: #ffffff;
        font-size: 1.35rem;
        margin: 0 0 0.75rem 0;
    }
    .how-step p {
        color: rgba(255, 255, 255, 0.78);
        line-height: 1.6;
        margin: 0;
        font-size: 0.95rem;
    }
    .features-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1.2rem;
    }
    .feature-card {
        min-height: 190px;
        border-radius: 16px;
        padding: 1.45rem;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.2);
    }
    .feature-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(135, 242, 206, 0.16);
        color: #87f2ce;
        font-size: 1.3rem;
        font-weight: 900;
        margin-bottom: 1.15rem;
    }
    .feature-card h3 {
        color: #ffffff;
        font-size: 1.25rem;
        margin: 0 0 0.7rem 0;
    }
    .feature-card p {
        color: rgba(255, 255, 255, 0.78);
        line-height: 1.6;
        margin: 0;
        font-size: 0.95rem;
    }
    @media (max-width: 900px) {
        .hero-nav {
            padding: 0 1.25rem;
        }
        .hero-links {
            display: none;
        }
        .hero-content {
            grid-template-columns: 1fr;
            padding: 3rem 1.6rem 5rem 1.6rem;
            gap: 2rem;
        }
        .score-float {
            justify-self: start;
            width: min(540px, 100%);
            min-height: auto;
            display: grid;
            gap: 1rem;
        }
        .hero-insight-card,
        .hero-insight-card.primary,
        .hero-insight-card.top,
        .hero-insight-card.bottom {
            position: static;
            width: 100%;
            min-height: auto;
        }
        .how-nav {
            padding: 0 1.25rem;
        }
        .how-content {
            padding: 4rem 1.4rem;
        }
        .how-steps {
            grid-template-columns: 1fr;
        }
        .features-grid {
            grid-template-columns: 1fr;
        }
    }
    @keyframes pageEnter {
        0% {
            opacity: 0;
            transform: translateX(28px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    @keyframes slideTitleIn {
        0% {
            opacity: 0;
            transform: translateX(-120px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    @keyframes fadeIn {
        0% {
            opacity: 0;
        }
        100% {
            opacity: 1;
        }
    }
    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(14px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """.replace("__HERO_BG__", hero_bg_data),
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

if st.query_params.get("started") == "1":
    st.session_state.started = True
    st.query_params.clear()

if not st.session_state.started:
    if st.query_params.get("page") == "how":
        st.markdown(
            """
            <div class="how-shell">
                <nav class="how-nav">
                    <a class="how-back" href="./" target="_self">Back to Home</a>
                    <a class="hero-nav-cta" href="?started=1" target="_self">Get Started</a>
                </nav>
                <main class="how-content">
                    <div class="how-kicker">How it works</div>
                    <h1 class="how-title">From resume to better fit in minutes.</h1>
                    <p class="how-intro">
                        HireLens compares your resume with the job description and turns the gap into clear,
                        realistic next steps. It helps you understand what already matches, what is weak,
                        and how to improve without keyword stuffing.
                    </p>
                    <div class="how-steps">
                        <section class="how-step">
                            <div class="how-number">1</div>
                            <h3>Add your resume</h3>
                            <p>Upload a PDF, DOCX, or TXT resume, or paste your resume text directly into the app.</p>
                        </section>
                        <section class="how-step">
                            <div class="how-number">2</div>
                            <h3>Add the job description</h3>
                            <p>Paste the full JD so HireLens can compare skills, responsibilities, eligibility, and role expectations.</p>
                        </section>
                        <section class="how-step">
                            <div class="how-number">3</div>
                            <h3>Get useful insights</h3>
                            <p>See your match score, strong matches, missing requirements, document needs, and targeted resume bullet suggestions.</p>
                        </section>
                    </div>
                </main>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    if st.query_params.get("page") == "features":
        st.markdown(
            """
            <div class="how-shell">
                <nav class="how-nav">
                    <a class="how-back" href="./" target="_self">Back to Home</a>
                    <a class="hero-nav-cta" href="?started=1" target="_self">Get Started</a>
                </nav>
                <main class="how-content">
                    <div class="how-kicker">Features</div>
                    <h1 class="how-title">Built for smarter resume tailoring.</h1>
                    <p class="how-intro">
                        HireLens goes beyond simple keyword checks. It reads your resume against the job description
                        and gives practical feedback you can actually use before applying.
                    </p>
                    <div class="features-grid">
                        <section class="feature-card">
                            <div class="feature-icon">%</div>
                            <h3>Alignment score</h3>
                            <p>Get a clear match percentage that reflects technical fit, role responsibilities, domain fit, and eligibility requirements.</p>
                        </section>
                        <section class="feature-card">
                            <div class="feature-icon">✓</div>
                            <h3>Strong match detection</h3>
                            <p>See which skills, tools, responsibilities, and experience areas already line up well with the job description.</p>
                        </section>
                        <section class="feature-card">
                            <div class="feature-icon">!</div>
                            <h3>Missing and weak areas</h3>
                            <p>Spot gaps in requirements, documents, location, schedule, eligibility, and technical skills before you submit.</p>
                        </section>
                        <section class="feature-card">
                            <div class="feature-icon">✎</div>
                            <h3>Targeted bullet improvements</h3>
                            <p>Receive realistic resume bullet suggestions with reasons, designed to improve fit without inventing experience.</p>
                        </section>
                        <section class="feature-card">
                            <div class="feature-icon">PDF</div>
                            <h3>Flexible resume input</h3>
                            <p>Upload PDF, DOCX, or TXT resumes, or paste resume text manually when you want a quick check.</p>
                        </section>
                        <section class="feature-card">
                            <div class="feature-icon">AI</div>
                            <h3>Truthfulness guardrails</h3>
                            <p>The feedback is designed to avoid keyword stuffing and only recommend additions when the experience is genuinely supported.</p>
                        </section>
                    </div>
                </main>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    st.markdown(
        """
        <div class="hero-shell">
            <nav class="hero-nav">
                <div></div>
                <div class="hero-links">
                    <a class="hero-link" href="?page=how" target="_self">How it works</a>
                    <a class="hero-link" href="?page=features" target="_self">Features</a>
                    <a class="hero-nav-cta" href="?started=1" target="_self">Get Started</a>
                </div>
            </nav>
            <section class="hero-content">
                <div class="hero-copy">
                    <div class="hero-eyebrow">AI-Powered Resume Matching</div>
                    <h1 class="landing-title">HireLens</h1>
                    <div class="landing-subtitle">
                        Get AI-powered insights, match your resume, and take the next step in your career.
                    </div>
                </div>
                <div class="score-float">
                    <div class="hero-insight-card top">
                        <div class="card-kicker">Resume Scan</div>
                        <div class="card-title">Key strengths found</div>
                        <div class="suggestion-bars">
                            <div class="suggestion-bar accent"></div>
                            <div class="suggestion-bar"></div>
                            <div class="suggestion-bar mid"></div>
                        </div>
                    </div>
                    <div class="hero-insight-card primary">
                        <div class="card-kicker">Match Score</div>
                        <div class="score-ring">
                            <div class="score-ring-number">89%</div>
                            <div class="score-ring-label">Great Match</div>
                        </div>
                        <div class="card-title">Strong fit for this role</div>
                        <div class="card-copy">Your resume already matches important requirements. HireLens highlights what to sharpen next.</div>
                    </div>
                    <div class="hero-insight-card bottom">
                        <div class="card-kicker">AI Suggestions</div>
                        <div class="card-title">3 high-impact edits</div>
                        <div class="card-copy">Improve weak JD areas with truthful, targeted resume bullet updates.</div>
                        <div class="metric-row">
                            <div>
                                <div class="metric-value">+18%</div>
                                <div class="metric-label">Potential lift</div>
                            </div>
                            <div>
                                <div class="metric-value">5</div>
                                <div class="metric-label">Missing items</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1480px !important;
        padding: 3.5rem 3.25rem 4rem 3.25rem !important;
        margin: 0 auto !important;
        animation: pageEnter 0.55s ease-out both;
    }
    div[data-testid="column"] {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.35rem 1.35rem 1.5rem 1.35rem;
        box-shadow: 0 22px 56px rgba(0, 0, 0, 0.18);
    }
    div[data-testid="column"] h3 {
        margin-top: 0;
    }
    div[data-testid="stFileUploader"] section,
    textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: #272832 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }
    div[data-testid="stFileUploader"] section button {
        border-radius: 10px !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        background: #111722 !important;
    }
    .stButton > button {
        height: 50px;
        margin-top: 1.15rem;
        border-radius: 10px;
        border: 0;
        background: #ff4b4f;
        color: #ffffff;
        font-weight: 850;
        box-shadow: 0 18px 40px rgba(255, 75, 79, 0.22);
        transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
    }
    .stButton > button:hover {
        background: #e83d42;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 22px 48px rgba(255, 75, 79, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    @media (max-width: 900px) {
        .block-container {
            padding: 1.5rem 1rem 3rem 1rem !important;
        }
        div[data-testid="column"] {
            padding: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<main class="analyzer-page">', unsafe_allow_html=True)
st.markdown('<a class="analyzer-back" href="./" target="_self">Back to Home</a>', unsafe_allow_html=True)
st.markdown('<div class="main-title">HireLens AI JD Aligner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtle">Upload your resume, paste the job description, and get an AI-powered match score with realistic improvement suggestions.</div>',
    unsafe_allow_html=True,
)

model = "llama-3.3-70b-versatile"

st.markdown('<div class="analyzer-spacer"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("1. Resume")
    uploaded_resume = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    resume_text_manual = st.text_area("Or paste resume text", height=280, placeholder="Paste resume text here...")

with col2:
    st.subheader("2. Job Description")
    jd_text = st.text_area("Paste JD", height=350, placeholder="Paste the full job description here...")

run_analysis = st.button("Analyze Resume Alignment", type="primary", use_container_width=True)
st.markdown("</main>", unsafe_allow_html=True)

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
