# outreach/generator.py
from groq import Groq
import os
from dotenv import load_dotenv
from scorer.resume_parser import extract_resume_text
from loguru import logger

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_email(job_title, company, job_description, recruiter):
    resume_text    = extract_resume_text()
    recruiter_name = recruiter.get("name", "Hiring Team")
    first_name     = recruiter_name.split()[0] if recruiter_name else "there"

    prompt = f"""You are helping a professional write a concise, personalized cold outreach email to a recruiter.

RECRUITER:
Name: {recruiter_name}
Title: {recruiter.get("title", "Recruiter")}
Company: {company}

JOB ROLE: {job_title}

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE RESUME:
{resume_text[:2000]}

INSTRUCTIONS:
- Write a 4-6 line email body ONLY (no fluff, no filler)
- Address recruiter by first name: Hi {first_name}
- Identify the 2 strongest alignment points between the resume and JD
- Lead with the most relevant experience, not "I saw your job posting"
- End with a single, low-friction CTA (15-minute call)
- Tone: confident, direct, peer-to-peer — not desperate or sycophantic
- Do NOT use: "I am excited", "I believe", "I am passionate", "perfect fit"
- Also write a punchy subject line under 10 words

Return in this exact format:
SUBJECT: <subject line>
BODY:
<email body>"""

    try:
        response = client.chat.completions.create(
            model    = "llama-3.1-8b-instant",   # free, fast
            messages = [{"role": "user", "content": prompt}],
            max_tokens = 500,
        )

        raw   = response.choices[0].message.content.strip()
        lines = raw.split("\n")

        subject = ""
        body    = ""

        for i, line in enumerate(lines):
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                body = "\n".join(lines[i+1:]).strip()
                break

        if not subject or not body:
            logger.warning(f"[Generator] Unexpected format for {job_title} @ {company}")
            return None

        logger.info(f"[Generator] Email generated for {job_title} @ {company}")
        return {"subject": subject, "body": body}

    except Exception as e:
        logger.error(f"[Generator] Groq API error: {e}")
        return None