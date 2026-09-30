import html
import os
import tempfile
from pathlib import Path

import requests
import streamlit as st

from dotenv import load_dotenv

from backend.services.document_service import (
    make_docx,
    make_pdf,
    make_txt
)


load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "120"
    )
)


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #111827,
                #1f2937
            );
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.4rem;
    }

    .hero p {
        margin-top: 0.4rem;
        color: #d1d5db;
        font-size: 1.05rem;
    }

    .preview-box {
        background: #111827;
        color: #f9fafb;
        padding: 1.5rem;
        border-radius: 15px;
        min-height: 500px;
        max-height: 700px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.7;
        font-size: 15px;
    }

    .legal-notice {
        padding: 1rem;
        margin-top: 1rem;
        border-left: 5px solid #64748b;
        background: #f8fafc;
        border-radius: 8px;
        color: #334155;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-assisted legal document drafting,
            editing and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = (
        "Legal Document"
    )


if "brand_name" not in st.session_state:

    st.session_state.brand_name = None


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("📄 Document Details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Service Agreement",
            "Employment Offer Letter",
            "General Agreement",
            "Custom"
        ]
    )


    if document_type == "Custom":

        document_type = st.text_input(
            "Custom Document Type",
            placeholder="Consulting Agreement"
        )


    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=120
    )


    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days;\n"
            "Confidentiality must be maintained;\n"
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help=(
            "Enter one term per line or separate "
            "terms using semicolons."
        )
    )


    effective_date = st.text_input(
        "Effective Date",
        placeholder="October 1, 2026"
    )


    brand_name = st.text_input(
        "Company / Brand Name",
        placeholder="TechNova Inc."
    )


    logo = st.file_uploader(
        "Upload Logo (Optional)",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    generate_button = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True
    )


# ---------------------------------------------------------
# Generate document
# ---------------------------------------------------------

if generate_button:

    missing_fields = []


    if not document_type.strip():

        missing_fields.append(
            "document type"
        )


    if not parties.strip():

        missing_fields.append(
            "parties"
        )


    if not terms.strip():

        missing_fields.append(
            "terms"
        )


    if not effective_date.strip():

        missing_fields.append(
            "effective date"
        )


    if missing_fields:

        st.error(
            "Please provide: "
            + ", ".join(missing_fields)
            + "."
        )

    else:

        payload = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date,

            "brand_name":
                brand_name or None
        }


        try:

            with st.spinner(
                "🤖 Generating document with Gemini..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )


            if response.ok:

                data = response.json()


                st.session_state.document = (
                    data["content"]
                )


                st.session_state.document_type = (
                    data["document_type"]
                )


                st.session_state.brand_name = (
                    brand_name or None
                )


                st.success(
                    "Document generated successfully. "
                    "Please review it carefully."
                )


            else:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text
                    )

                except Exception:

                    detail = response.text


                st.error(
                    f"Backend error "
                    f"({response.status_code}): "
                    f"{detail}"
                )


        except requests.RequestException as error:

            st.error(
                "Could not connect to the FastAPI backend.\n\n"
                f"Backend URL: {BACKEND_URL}\n\n"
                f"Error: {error}"
            )


# ---------------------------------------------------------
# Preview
# ---------------------------------------------------------

st.subheader("📑 Document Preview")


if st.session_state.document:

    preview_column, edit_column = st.columns(
        [3, 1]
    )


    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    with preview_column:

        safe_document = html.escape(
            st.session_state.document
        )


        st.markdown(
            f"""
            <div class="preview-box">
                {safe_document}
            </div>
            """,
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # Editor
    # -----------------------------------------------------

    with edit_column:

        st.markdown("### ✏️ Edit")

        edited_document = st.text_area(
            "Edit document",
            value=st.session_state.document,
            height=500,
            label_visibility="collapsed"
        )


        if st.button(
            "Apply Changes",
            use_container_width=True
        ):

            st.session_state.document = (
                edited_document
            )

            st.rerun()


    # -----------------------------------------------------
    # Legal notice
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="legal-notice">

        <strong>AI Draft Notice</strong><br>

        This document was generated with AI assistance.
        It is not legal advice and should be reviewed by
        a qualified legal professional before signing or
        relying upon it.

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # Downloads
    # -----------------------------------------------------

    st.subheader("⬇️ Download")


    with tempfile.TemporaryDirectory() as temp_dir:

        logo_path = None


        if logo is not None:

            extension = (
                Path(logo.name).suffix.lower()
                or ".png"
            )


            logo_path = os.path.join(
                temp_dir,
                f"logo{extension}"
            )


            with open(
                logo_path,
                "wb"
            ) as file:

                file.write(
                    logo.getbuffer()
                )


        txt_file = make_txt(
            st.session_state.document
        )


        docx_file = make_docx(
            text=st.session_state.document,
            doc_type=st.session_state.document_type,
            brand_name=st.session_state.brand_name,
            logo_path=logo_path,
            terms=terms
        )


        pdf_file = make_pdf(
            text=st.session_state.document,
            doc_type=st.session_state.document_type,
            brand_name=st.session_state.brand_name,
            logo_path=logo_path
        )


    # -----------------------------------------------------
    # Filename
    # -----------------------------------------------------

    filename = "".join(

        character.lower()
        if character.isalnum()
        else "_"

        for character
        in st.session_state.document_type
    )


    filename = (
        filename.strip("_")
        or "legal_document"
    )


    # -----------------------------------------------------
    # Download buttons
    # -----------------------------------------------------

    download_txt, download_docx, download_pdf = (
        st.columns(3)
    )


    with download_txt:

        st.download_button(
            "⬇️ Download TXT",
            data=txt_file,
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True
        )


    with download_docx:

        st.download_button(
            "⬇️ Download DOCX",
            data=docx_file,
            file_name=f"{filename}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True
        )


    with download_pdf:

        st.download_button(
            "⬇️ Download PDF",
            data=pdf_file,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


else:

    st.info(
        "Enter your document information in the "
        "left sidebar and click **Generate Document**."
    )