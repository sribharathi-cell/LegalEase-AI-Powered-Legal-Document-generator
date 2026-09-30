from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=12000
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    brand_name: Optional[str] = Field(
        default=None,
        max_length=200
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date"
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("brand_name")
    @classmethod
    def validate_brand_name(
        cls,
        value: Optional[str]
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value if value else None


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    disclaimer: str