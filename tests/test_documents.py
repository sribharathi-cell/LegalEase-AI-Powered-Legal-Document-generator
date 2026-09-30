from backend.services.document_service import (
    make_docx,
    make_pdf,
    make_txt,
    parse_terms,
    sanitize_text
)


SAMPLE_DOCUMENT = """
NON-DISCLOSURE AGREEMENT

PARTIES

Jane Doe and Example Corporation.

1. CONFIDENTIALITY

Confidential information must be protected.

2. TERM

This agreement remains effective for two years.

AI DRAFT NOTICE

This is an AI-generated draft.
"""


def test_sanitize_text():

    result = sanitize_text(
        "Hello\u2014World"
    )

    assert result == "Hello-World"


def test_parse_terms():

    result = parse_terms(
        "Payment within 30 days; "
        "Confidentiality required\n"
        "Termination with notice"
    )

    assert len(result) == 3


def test_txt_export():

    result = make_txt(
        SAMPLE_DOCUMENT
    )

    assert isinstance(
        result,
        bytes
    )

    assert (
        b"NON-DISCLOSURE AGREEMENT"
        in result
    )


def test_docx_export():

    result = make_docx(
        text=SAMPLE_DOCUMENT,
        doc_type="Non-Disclosure Agreement"
    )

    assert isinstance(
        result,
        bytes
    )

    # DOCX is a ZIP container
    assert result[:2] == b"PK"


def test_pdf_export():

    result = make_pdf(
        text=SAMPLE_DOCUMENT,
        doc_type="Non-Disclosure Agreement"
    )

    assert isinstance(
        result,
        bytes
    )

    assert result.startswith(
        b"%PDF"
    )