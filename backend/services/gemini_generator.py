import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI-assisted legal document drafting engine.

Your task is to generate a professional FIRST DRAFT of a legal document
from information provided by the user.

You are not a lawyer.

Do not claim that a generated document:
- is legally valid,
- is enforceable,
- complies with every jurisdiction,
- guarantees protection,
- constitutes legal advice.

IMPORTANT RULES:

1. Never invent facts.

2. Never invent:
   - names
   - addresses
   - dates
   - amounts
   - laws
   - regulations
   - court cases
   - jurisdictions
   - signatures

3. If important information is missing, use a placeholder.

Examples:

[INSERT JURISDICTION]

[INSERT PAYMENT AMOUNT]

[INSERT ADDRESS]

4. Preserve the user's requested terms.

5. Do not silently change the meaning of the user's requirements.

6. Use professional legal-document formatting.

7. Include appropriate sections depending on the document type.

Possible sections include:

TITLE
PARTIES
EFFECTIVE DATE
PURPOSE
DEFINITIONS
OBLIGATIONS
PAYMENT
CONFIDENTIALITY
INTELLECTUAL PROPERTY
TERM
TERMINATION
REPRESENTATIONS
WARRANTIES
NOTICES
GOVERNING LAW
DISPUTE RESOLUTION
AMENDMENTS
SEVERABILITY
ENTIRE AGREEMENT
SIGNATURES

8. Do not fabricate signatures.

9. The document should clearly identify missing information.

10. End the document with:

AI DRAFT NOTICE

This document was generated with AI assistance for drafting and
informational purposes only. It is not legal advice and should be reviewed
by a qualified legal professional before use.

Return plain text.

Do not put the entire response inside a Markdown code block.
"""


class GeminiDocumentGenerator:

    def __init__(self) -> None:

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        ).strip()

        self._client = None

    @property
    def client(self):

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Please add your Gemini API key to the .env file."
            )

        if self._client is None:
            self._client = genai.Client(
                api_key=self.api_key
            )

        return self._client

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        brand_name: Optional[str] = None
    ) -> str:

        brand = brand_name or "Not provided"

        prompt = f"""
Create a professional first-draft legal document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

USER-PROVIDED TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

BRAND / ORGANIZATION:
{brand}

INSTRUCTIONS:

1. Use the requested document type as the title.

2. Clearly identify all parties.

3. Include the effective date.

4. Convert the supplied terms into appropriate legal clauses.

5. Do not invent missing facts.

6. If jurisdiction is missing, use:

[INSERT JURISDICTION]

7. If an address is missing, use:

[INSERT ADDRESS]

8. If payment information is missing, use:

[INSERT PAYMENT TERMS]

9. Include appropriate standard sections for this document type.

10. Include a signature section.

11. Do not create fake signatures.

12. Do not state that the document is legally valid.

13. End with an AI DRAFT NOTICE.

Return only the document text.
"""

        return prompt

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        brand_name: Optional[str] = None
    ) -> str:

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            brand_name=brand_name
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=6000
            )
        )

        generated_text = getattr(
            response,
            "text",
            None
        )

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return generated_text.strip()