import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from backend.services.document_service import generate_document


st.set_page_config(
    page_title="LegalEase AI",
    page_icon="⚖️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .warning-box {
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        padding: 15px;
        border-radius: 8px;
        color: #9a3412;
        margin-bottom: 20px;
    }

    .document-box {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 25px;
        line-height: 1.7;
        font-family: Georgia, "Times New Roman", serif;
        white-space: pre-wrap;
    }

    .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #6b7280;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">⚖️ LegalEase AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        AI-Powered Legal Document Generator
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="warning-box">
        <strong>Important:</strong>
        LegalEase AI generates first-draft legal documents for
        informational and drafting purposes only. It does not
        provide legal advice. Please have the generated document
        reviewed by a qualified legal professional before use.
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:

    st.header("Document Settings")

    document_type = st.selectbox(
        "Document Type",
        [
            "Non-Disclosure Agreement",
            "Employment Agreement",
            "Service Agreement",
            "Consulting Agreement",
            "Freelance Agreement",
            "Rental Agreement",
            "Partnership Agreement",
            "Privacy Policy",
            "Terms and Conditions",
            "Other",
        ],
    )

    brand_name = st.text_input(
        "Brand / Organization",
        placeholder="Example: ABC Technologies",
    )

    st.markdown("---")

    st.write(
        "Select the type of legal document you want to generate."
    )


st.header("Create Your Legal Document")

col1, col2 = st.columns(2)


with col1:

    st.subheader("Parties")

    parties = st.text_area(
        "Enter the parties involved",
        placeholder=(
            "Example:\n"
            "Party A: [INSERT NAME]\n"
            "Party B: [INSERT NAME]"
        ),
        height=180,
    )


with col2:

    st.subheader("Effective Date")

    effective_date = st.text_input(
        "Enter effective date",
        placeholder="Example: [INSERT EFFECTIVE DATE]",
    )


st.subheader("Terms and Conditions")

terms = st.text_area(
    "Describe the requirements of the document",
    placeholder=(
        "Enter the terms, conditions, obligations, "
        "payment details, confidentiality requirements, "
        "termination conditions, and other information."
    ),
    height=250,
)


st.markdown("---")


generate_button = st.button(
    "⚖️ Generate Legal Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter the effective date."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    else:

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                generated_document = generate_document(
                    document_type=document_type,
                    parties=parties,
                    terms=terms,
                    effective_date=effective_date,
                    brand_name=brand_name or None,
                )

                if not generated_document:
                    raise RuntimeError(
                        "The AI returned an empty response."
                    )

                st.session_state[
                    "generated_document"
                ] = generated_document

                st.success(
                    "Document generated successfully."
                )

            except Exception as error:

                st.error(
                    "Document generation failed."
                )

                st.exception(error)


generated_document = st.session_state.get(
    "generated_document"
)


if generated_document:

    st.markdown("---")

    st.header("Document Preview")

    safe_document = (
        generated_document
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    st.markdown(
        '<div class="document-box">'
        + safe_document
        + "</div>",
        unsafe_allow_html=True,
    )


    st.markdown("---")

    st.subheader("Download Document")

    download_col1, download_col2, download_col3 = st.columns(3)


    with download_col1:

        txt_data = generated_document.encode(
            "utf-8"
        )

        st.download_button(
            label="⬇️ Download TXT",
            data=txt_data,
            file_name="legal_document.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with download_col2:

        try:

            from io import BytesIO
            from docx import Document

            docx_document = Document()

            for paragraph in generated_document.split("\n"):
                docx_document.add_paragraph(paragraph)

            docx_buffer = BytesIO()

            docx_document.save(docx_buffer)

            docx_buffer.seek(0)

            st.download_button(
                label="⬇️ Download DOCX",
                data=docx_buffer.getvalue(),
                file_name="legal_document.docx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as error:

            st.error(
                f"DOCX generation failed: {error}"
            )


    with download_col3:

        try:

            from io import BytesIO

            from reportlab.lib.pagesizes import A4

            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
            )

            from reportlab.lib.styles import (
                getSampleStyleSheet,
            )

            pdf_buffer = BytesIO()

            pdf = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=45,
                leftMargin=45,
                topMargin=45,
                bottomMargin=45,
            )

            styles = getSampleStyleSheet()

            story = []

            for line in generated_document.split("\n"):

                if line.strip():

                    safe_line = (
                        line
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )

                    story.append(
                        Paragraph(
                            safe_line,
                            styles["BodyText"],
                        )
                    )

                    story.append(
                        Spacer(1, 8)
                    )

                else:

                    story.append(
                        Spacer(1, 10)
                    )

            pdf.build(story)

            pdf_buffer.seek(0)

            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_buffer.getvalue(),
                file_name="legal_document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as error:

            st.error(
                f"PDF generation failed: {error}"
            )


st.markdown(
    """
    <div class="footer">
        <strong>LegalEase AI</strong><br>
        AI-assisted legal document drafting tool.<br><br>
        This application does not provide legal advice.
        Generated documents should be reviewed by a qualified
        legal professional before use.
    </div>
    """,
    unsafe_allow_html=True,
)