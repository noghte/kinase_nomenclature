#TODO: for each function, if is called by LLM, provide a few examples of the output
from langchain_core.tools import tool
from utils import Section, extract_pdf_text

@tool
def load_pdf(pdf_path: str) -> str:
    """
    Load PDF and extract all text as string.
    """
    return extract_pdf_text(pdf_path)

@tool
def extract_name_and_synonyms(protein_name: str,  pdf_text: str) -> str:
    """
    Extract EC number, accepted name, and synonyms for the specified protein.
    """
    prompt = f"Extract EC number, accepted name, and synonyms for {protein_name}."
    return Section.NAME_AND_SYNONYMS.ask(prompt, pdf_text)

@tool
def extract_gene_location(protein_name: str, name_and_synonyms: str,  pdf_text: str) -> str:
    """
    Extract gene location information, species, and expression patterns for the specified protein.
    """
    prompt = f"Extract gene location, species, and expression patterns for {protein_name}."
    return Section.GENE_LOCATION.ask(prompt, pdf_text)

@tool
def extract_structure_info(protein_name: str, name_and_synonyms: str,  pdf_text: str) -> str:
    """
    Extract structural information about the specified protein including domain organization and binding sites.
    """
    prompt = (
        f"Describe the structure of {protein_name} including domain organization, motifs, and binding sites. "
        f"Is there information related to conformational changes associated with regulatory functions or residues associated with catalytic or regulatory functions? "
        f"Can you find mentions of specific structural interactions such as hydrogen bonds, electrostatic, or van der Waals interactions associated with structure, stability or conformation?"
    )
    return Section.STRUCTURE.ask(prompt, pdf_text)

@tool
def extract_function_info(protein_name: str, name_and_synonyms: str,  pdf_text: str) -> str:
    """
    Extract functional information about the specified protein including pathways and phosphorylation targets.
    """
    prompt = (
        f"Describe the function of {protein_name} with a focus on its substrates and pathways. "
        f"What are the known substrates of the {protein_name}? "
        f"What is the substrate specificity of {protein_name}? "
        f"Where is {protein_name} expressed, and what is the function of {protein_name} in different cells or tissue types? "
        f"Which regulatory pathways is {protein_name} involved in?"
    )
    return Section.FUNCTION.ask(prompt, pdf_text)

@tool
def extract_regulation_info(protein_name: str, name_and_synonyms: str,  pdf_text: str) -> str:
    """
    Extract information about how the specified protein is regulated through phosphorylation and other mechanisms.
    """
    prompt = (
        f"Outline how {protein_name} is regulated, phosphorylation sites, and regulators."\
        f" At which sites/amino acids is {protein_name} phosphorylated? Which proteins phosphorylate {protein_name}? What is the mechasim?"\
        f"How {protein_name} is activated or repressed?"
    )
    return Section.REGULATION.ask(prompt, pdf_text)

@tool
def extract_specificity_info(protein_name: str, name_and_synonyms: str,  pdf_text: str) -> str:
    """
    Extract information about the substrate specificity of the specified protein including phosphorylation targets.
    """
    prompt = (
    f"Outline how {protein_name} is regulated by post-translational modifications. "
    f"At which sites/amino acids is {protein_name} modified? "
    f"Which proteins phosphorylate {protein_name}? What is the mechanism? "
    f"How is {protein_name} activated or repressed in pathways?"
    )
    return Section.SPECIFICITY.ask(prompt, pdf_text)

@tool
def get_phylogeny(protein_name: str) -> str:
    """
    Return phylogenetic information for the protein.
    """
    # We don't need papers for this question, we can use 
    #Get Group, family, and subfamily from the excel file. 
    return "To be implemented"

@tool
def get_reaction_catalyzed(protein_name: str) -> str:
    """
    Return reaction catalyzed by the protein.
    """
    # It comes directly from uniprot. (the section name is Catalytic activity), Example for BRSK1 is the first two, because it has only [protein] in the text (not the [tau protein])
    return "To be implemented"

@tool
def get_cofactor_requirements(protein_name: str) -> str:
    """
    Return cofactor requirements for the protein.
    """
    # Cofactor requirments: from unirpot (Cofactor section)
    return "To be implemented"

@tool
def get_inhibitors(protein_name: str) -> str:
    """
    Return known inhibitors of the protein.
    """
    return f"To be implemented (by calling KLIFS) to answer: What inhibits the activity of {protein_name}? "

@tool
def get_db_links(protein_name: str) -> str:
    """
    Return database links for the protein.
    """
    return "To be implemented"