from pathlib import Path

import PyPDF2


class ResumeParser:
    """Extracts plain text from PDF, DOCX and TXT resumes."""

    def parse(self, file_path) -> str:
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf(file_path)
        if suffix == ".docx":
            return self._extract_docx(file_path)
        if suffix == ".txt":
            return self._extract_txt(file_path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_pdf(self, file_path: Path) -> str:
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    def _extract_docx(self, file_path: Path) -> str:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(
            para.text for para in doc.paragraphs
        ).strip()

    def _extract_txt(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8", errors="ignore").strip()
