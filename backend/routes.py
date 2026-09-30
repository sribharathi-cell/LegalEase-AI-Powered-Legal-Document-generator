import os

from fastapi import APIRouter, HTTPException

from .schemas import (
    DocumentRequest,
    DocumentResponse
)

from .services.gemini_generator import (
    GeminiDocumentGenerator
)


router = APIRouter()

generator = GeminiDocumentGenerator()


DISCLAIMER = (
    "AI-generated draft only. Review all content with a qualified "
    "legal professional before relying on or signing it."
)


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "LegalEase API",
        "gemini_configured": bool(
            os.getenv(
                "GEMINI_API_KEY",
                ""
            ).strip()
        ),
        "model": generator.model
    }


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            brand_name=request.brand_name
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            model=generator.model,
            disclaimer=DISCLAIMER
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {error}"
        ) from error