import re
import io


def extract_text(file_obj, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "txt":
        raw = file_obj.read()
        return raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw

    elif ext == "pdf":
        import pypdf
        reader = pypdf.PdfReader(file_obj)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext == "docx":
        import docx2txt
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_obj.read())
            tmp_path = tmp.name
        try:
            text = docx2txt.process(tmp_path)
        finally:
            os.unlink(tmp_path)
        return text

    else:
        raise ValueError(f"Unsupported file type: .{ext}")


_LEGAL_HEADERS = re.compile(
    r"(?m)^(?=\s*(?:\d+\.|\([a-z]\)|\b(?:WHEREAS|NOW THEREFORE|SECTION|ARTICLE|"
    r"Limitation of Liability|Indemnification|Governing Law|Confidentiality|"
    r"Term and Termination|Warranty|Intellectual Property|Payment|Assignment|"
    r"Force Majeure|Dispute Resolution|Notices|General)\b))",
    re.IGNORECASE,
)


def chunk_contract(text: str, min_len: int = 80) -> list[str]:
    # Split on legal section headers first, then fall back to double newlines
    parts = _LEGAL_HEADERS.split(text)
    if len(parts) < 3:
        parts = re.split(r"\n\s*\n", text)

    chunks = []
    for part in parts:
        part = part.strip()
        if len(part) >= min_len:
            chunks.append(part)

    return chunks
