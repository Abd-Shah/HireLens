# HireLens — AI JD Aligner

HireLens is an AI-powered tool that evaluates how well a resume matches a specific job posting. Upload a resume, paste a job description, and get an AI-generated match score with targeted, truthful improvement suggestions — no fabricated experience, no keyword stuffing.

**Live app:** [hirelensmatch.streamlit.app](https://hirelensmatch.streamlit.app)
<img width="1815" height="728" alt="Screenshot 2026-08-09 at 3 50 35 AM" src="https://github.com/user-attachments/assets/eabfb3fa-3fe1-4dac-8761-a642fcf4e9fc" />


## Why HireLens

Most resume-matching tools either give a vague percentage score or blindly suggest stuffing in keywords from the job description, regardless of whether the candidate actually has that experience. HireLens is built around a **truthfulness guardrail**: it only recommends adding a skill or requirement if there's evidence in the resume that the candidate genuinely has it. The goal is a more honest, defensible resume — not a higher score at the cost of accuracy.

## Features

- Upload resumes in PDF, DOCX, or TXT format
- Paste any job description for comparison
- AI-generated resume-to-JD alignment score
- Identifies strong matches between resume content and job requirements
- Highlights missing or weak requirements
- Suggests targeted resume bullet improvements
- Truthfulness guardrails — never invents experience or recommends unsupported keyword stuffing

## How It Works

1. **Text extraction** — the uploaded resume is parsed and converted to plain text (PDF/DOCX/TXT supported)
2. **Comparison** — the resume text and job description are sent to an LLM (via the Groq API) with a structured prompt designed to identify overlaps, gaps, and weak phrasing
3. **Scoring** — the model returns a match score along with categorized findings: strong matches, missing requirements, and weak/underdeveloped bullet points
4. **Guardrailed suggestions** — before surfacing a suggestion, the prompt constrains the model to only recommend additions that are traceable to something already in the resume, avoiding fabricated qualifications

## Tech Stack

- **Frontend/App:** Streamlit
- **Language:** Python
- **LLM:** Groq API
- **Document parsing:** PDF/DOCX text extraction
- **Deployment:** Streamlit Cloud
