from langchain_core.tools import tool
from utils import Section, extract_pdf_text

@tool
def load_pdf(pdf_path: str) -> str:
    """
    Load PDF and extract all text as string.
    """
    return extract_pdf_text(pdf_path)

@tool
def extract_name_and_synonyms(protein_name: str, pdf_text: str) -> str:
    """
    Extract EC number, accepted name, and synonyms for the specified protein.
    """
    prompt = f"Extract EC number, accepted name, and synonyms for {protein_name}."
    return Section.NAME_AND_SYNONYMS.ask(prompt, pdf_text)

@tool
def extract_gene_location(protein_name: str, pdf_text: str) -> str:
    """
    Extract gene location information, species, and expression patterns for the specified protein.
    """
    prompt = f"Extract gene location, species, and expression patterns for {protein_name}."
    return Section.GENE_LOCATION.ask(prompt, pdf_text)

@tool
def extract_structure_info(protein_name: str, pdf_text: str) -> str:
    """
    Extract structural information about the specified protein including domain organization and binding sites.
    """
    prompt = (
        f"Describe the structure of {protein_name} including domain organization, motifs, and binding sites."
    )
    return Section.STRUCTURE.ask(prompt, pdf_text)

@tool
def extract_function_info(protein_name: str, pdf_text: str) -> str:
    """
    Extract functional information about the specified protein including pathways and phosphorylation targets.
    """
    prompt = (
        f"Describe the function of {protein_name}, its pathways, and targets."
    )
    return Section.FUNCTION.ask(prompt, pdf_text)

@tool
def extract_regulation_info(protein_name: str, pdf_text: str) -> str:
    """
    Extract information about how the specified protein is regulated through phosphorylation and other mechanisms.
    """
    prompt = (
        f"Outline how {protein_name} is regulated, phosphorylation sites, and regulators."
    )
    return Section.REGULATION.ask(prompt, pdf_text)

@tool
def extract_specificity_info(protein_name: str, pdf_text: str) -> str:
    """
    Extract information about the substrate specificity of the specified protein including phosphorylation targets.
    """
    prompt = (
        f"Detail substrate specificity of {protein_name}, including motif preferences."
    )
    return Section.SPECIFICITY.ask(prompt, pdf_text)

@tool
def get_phylogeny(protein_name: str) -> str:
    """
    Return phylogenetic information for the protein.
    """
    return "To be implemented"

@tool
def get_reaction_catalyzed(protein_name: str) -> str:
    """
    Return reaction catalyzed by the protein.
    """
    return "To be implemented"

@tool
def get_cofactor_requirements(protein_name: str) -> str:
    """
    Return cofactor requirements for the protein.
    """
    return "To be implemented"

@tool
def get_inhibitors(protein_name: str) -> str:
    """
    Return known inhibitors of the protein.
    """
    return "To be implemented"

@tool
def get_db_links(protein_name: str) -> str:
    """
    Return database links for the protein.
    """
    return "To be implemented"