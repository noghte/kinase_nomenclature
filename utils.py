#TODO: Only include relevant context for each section
from enum import Enum
import fitz  # pymupdf
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv() 

llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

class Section(Enum):
    STRUCTURE = "Structure"
    FUNCTION = "Function"
    REGULATION = "Regulation"
    SPECIFICITY = "Specificity"
    NAME_AND_SYNONYMS = "Name and Synonyms"
    GENE_LOCATION = "Gene Location"

    def ask(self, prompt: str, context: str) -> str:
        """
        Send a combined prompt and context snippet to the LLM and return its response.
        """
        system_msg = HumanMessage(content=f"[Section: {self.value}]\n{prompt}")
        user_msg   = HumanMessage(content=context[:200] + "...")
        response   = llm.invoke([system_msg, user_msg])
        return response.content

def extract_pdf_text(pdf_path: str) -> str:
    """
    Load the PDF file at pdf_path and extract all text as a single string.
    """
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        text = page.get_text()
        if text:
            all_text.append(text)
    doc.close()
    return "\n".join(all_text)