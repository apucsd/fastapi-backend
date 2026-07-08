import json
from typing import Any, Dict
from openai import OpenAI
from app.core.config import openai_api_key
from app.utils.exceptions import AppException

MODELS = [
    "openai/gpt-oss-20b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "google/gemma-3-4b-it:free",
    "arcee-ai/trinity-mini:free",
    "gpt-oss-120b",
]


class AIService:
    def __init__(self):
        if not openai_api_key:
            raise AppException(
                status_code=500,
                message="OpenRouter API key not set"
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openai_api_key
        )

    async def extract_resume_data(
        self,
        resume_text: str
    ) -> Dict[str, Any]:
        last_error: Exception | None = None

        for model in MODELS:
            try:
                print(
                    f"Calling AI model={model} with text from PDF (length: {len(resume_text)})"
                )

                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert resume parser. "
                                "Return only valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": self._build_extraction_prompt(
                                resume_text
                            ),
                        },
                    ],
                )

                print("AI response received")

                choices = getattr(response, "choices", None)
                if not choices:
                    raise AppException(
                        status_code=502,
                        message="AI provider returned no choices",
                    )

                content = choices[0].message.content

                if not content:
                    raise AppException(
                        status_code=500,
                        message="Empty AI response",
                    )

                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    content = content[start : end + 1]

                return json.loads(content)

            except Exception as e:
                last_error = e
                print(f"AI model failed ({model}): {e}")

        raise AppException(
            status_code=502,
            message=f"All AI models failed. Last error: {last_error}",
        )

    def _build_extraction_prompt(
        self,
        raw_text: str
    ) -> str:
        return f"""
Extract structured information from the resume.

Return JSON in this exact format:

{{
  "skills": [],
  "education": [
    {{
      "institution": "",
      "degree": "",
      "years": ""
    }}
  ],
  "experience": [
    {{
      "company": "",
      "role": "",
      "years": "",
      "description": ""
    }}
  ]
}}

Resume:
{raw_text[:12000]}
"""

    async def score_job_match(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
    ) -> Dict[str, Any]:
        last_error: Exception | None = None

        for model in MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert job-resume matcher. "
                                "Return only valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": self._build_match_prompt(
                                resume_text, job_title, job_description
                            ),
                        },
                    ],
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    content = content[start : end + 1]

                return json.loads(content)

            except Exception as e:
                last_error = e
                print(f"AI match scoring failed ({model}): {e}")

        raise AppException(
            status_code=502,
            message=f"All AI models failed for job matching. Last error: {last_error}",
        )

    def _build_match_prompt(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
    ) -> str:
        return f"""
Compare this resume against the job posting and score the match.

Return JSON in this exact format:
{{
  "match_score": 0,
  "matching_skills": [],
  "missing_skills": [],
  "recommendation": ""
}}

Rules:
- match_score is an integer from 0 to 100
- matching_skills: skills the candidate HAS that the job REQUIRES
- missing_skills: skills the job REQUIRES that the candidate LACKS
- recommendation: one sentence of advice for the candidate

Resume:
{resume_text[:8000]}

Job Title: {job_title}
Job Description:
{job_description[:4000]}
"""

    async def generate_cover_letter(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str,
    ) -> str:
        last_error: Exception | None = None

        for model in MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert cover letter writer. "
                                "Write professional, personalized cover letters. "
                                "Return only the cover letter text, no JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": self._build_cover_letter_prompt(
                                resume_text, job_title, company, job_description
                            ),
                        },
                    ],
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                return content.strip()

            except Exception as e:
                last_error = e
                print(f"Cover letter generation failed ({model}): {e}")

        raise AppException(
            status_code=502,
            message=f"All AI models failed for cover letter. Last error: {last_error}",
        )

    def _build_cover_letter_prompt(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str,
    ) -> str:
        return f"""
Write a professional cover letter for a candidate applying to the following job.

Rules:
- Personalize it using the candidate's actual skills and experience from their resume
- Mention the company name and job title
- Keep it concise (3-4 paragraphs)
- Sound professional but not robotic
- Highlight how the candidate's experience directly matches the job requirements
- Do NOT include placeholder text like [Your Name] — use details from the resume

Resume:
{resume_text[:8000]}

Job Title: {job_title}
Company: {company}
Job Description:
{job_description[:4000]}
"""