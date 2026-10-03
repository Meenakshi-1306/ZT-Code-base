import os
import re
import fitz


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def identify_standard(filename: str):
    name = filename.lower()

    if "iso" in name:
        return {
            "standard": "ISO/IEC 27001",
            "version": "2022",
        }

    if "nist" in name:
        return {
            "standard": "NIST SP 800",
            "version": None,
        }

    if "cis" in name:
        return {
            "standard": "CIS Controls",
            "version": "v8.1",
        }

    if "pci" in name:
        return {
            "standard": "PCI DSS",
            "version": "4.0.1",
        }

    if "gdpr" in name:
        return {
            "standard": "GDPR",
            "version": "2016/679",
        }

    if "hipaa" in name:
        return {
            "standard": "HIPAA Security Rule",
            "version": None,
        }

    return {
        "standard": "Unknown",
        "version": None,
    }


def extract_pdf(pdf_path: str):
    document = fitz.open(pdf_path)

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):

            text = clean_text(page.get_text())

            if not text:
                continue

            pages.append({
                "page": page_number,
                "text": text,
            })

    finally:
        document.close()

    return pages


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150,
):
    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def process_pdf(
    pdf_path: str,
    organization_id: str,
    document_id: str,
):
    """
    Extract PDF text, split it into chunks,
    and attach organization/document metadata.
    """

    filename = os.path.basename(pdf_path)

    standard_info = identify_standard(filename)

    pages = extract_pdf(pdf_path)

    documents = []

    chunk_id = 0

    for page_data in pages:

        chunks = chunk_text(
            page_data["text"]
        )

        for chunk in chunks:

            documents.append({
                "text": chunk,

                "metadata": {
                    "source": filename,
                    "document_id": document_id,
                    "organization_id": organization_id,
                    "standard": standard_info["standard"],
                    "version": standard_info["version"],
                    "page": page_data["page"],
                    "chunk_id": chunk_id,
                },
            })

            chunk_id += 1

    return {
        "documents": documents,
        "pages": len(pages),
        "chunks": len(documents),
        "standard": standard_info["standard"],
        "version": standard_info["version"],
    }