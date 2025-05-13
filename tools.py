from langchain_core.tools import tool
from utils import Section, extract_pdf_text

@tool
def extract_structure(protein_name: str, pdf_text: str) -> str:
    prompt = f"""
    Describe the structure of {protein_name} in a format similar to the example. 
    Include details like domain organization, number of amino acids, molecular weight, conserved or regulatory motifs, and important binding sites if mentioned.
    """
    return Section.STRUCTURE.ask(prompt, context=pdf_text)


@tool
def extract_function(protein_name: str, pdf_text: str) -> str:
    prompt = f"""
    What is the function of {protein_name} in the body?
    Where is it expressed (organs/tissues)?
    What pathways is it involved in?
    Describe the functions of the proteins it phosphorylates.
    """
    return Section.FUNCTION.ask(prompt, context=pdf_text)


@tool
def extract_regulation(protein_name: str, pdf_text: str) -> str:
    prompt = f"""
    At which sites is {protein_name} phosphorylated?
    Which proteins phosphorylate it?
    What mechanisms regulate its activity (activation/inhibition)?
    """
    return Section.REGULATION.ask(prompt, context=pdf_text)


@tool
def extract_specificity(protein_name: str, pdf_text: str) -> str:
    prompt = f"""
    What is the substrate specificity of {protein_name}?
    What proteins does it phosphorylate?
    Which amino acid residues does it target?
    Are there motif preferences?
    """
    return Section.SPECIFICITY.ask(prompt, context=pdf_text)


# Stubbed tools for sections not yet implemented
@tool
def extract_phylogeny(protein_name: str) -> str:
    return "To be implemented"


@tool
def extract_reaction(protein_name: str) -> str:
    return "To be implemented"


@tool
def extract_cofactors(protein_name: str) -> str:
    return "To be implemented (data from uniprot)"


@tool
def extract_inhibitors(protein_name: str) -> str:
    return "To be implemented (data from KLIFS)"


@tool
def extract_links(protein_name: str) -> str:
    return "To be implemented (data from uniprot)"