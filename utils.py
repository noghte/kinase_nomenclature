from enum import Enum
import fitz  # pymupdf

class Section(Enum):
    STRUCTURE = "Structure"
    FUNCTION = "Function"
    REGULATION = "Regulation"
    SPECIFICITY = "Specificity"

    def ask(self, prompt: str, context: str) -> str:
        # Placeholder for future LLM call
        return f"\n[Prompt]\n{prompt}\n\n[Context]\n{context[:1000]}..."


def extract_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        text = page.get_text()
        if text:
            all_text.append(text)
    doc.close()
    return "\n".join(all_text)
