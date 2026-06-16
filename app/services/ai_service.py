import json
from typing import Any, Dict
from openai import OpenAI
from app.core.config import openai_api_key
from app.utils.exceptions import AppException

MODELS = [
    "qwen/qwen3.6-plus:free",
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