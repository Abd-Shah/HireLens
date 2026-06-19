# HireLens AI JD Aligner

A Streamlit app that compares a resume against a job description, gives an alignment percentage, and generates targeted resume improvement suggestions without keyword stuffing.

## Features

- Upload resume as PDF, DOCX, or TXT
- Paste a job description
- AI-powered JD/resume comparison
- Overall alignment score
- Strong matches
- Missing or weak requirements
- Targeted bullet improvements with reasons
- Truthfulness guardrails so the app does not invent experience

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

Run:

```bash
streamlit run app.py
```

## Important

The app is designed to suggest realistic improvements. It should not blindly paste missing JD keywords into every bullet. If a requirement is missing and not supported by the resume, it recommends adding it only if the candidate truly has that experience.
