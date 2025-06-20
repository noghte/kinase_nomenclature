#!/usr/bin/env python3
import os
import pypandoc
from pathlib import Path
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# where your raw .txt files live
INPUT_DIR      = Path("./futurehouse/outputs")
# where formatted results will be written
FORMATTED_DIR  = Path("./futurehouse/formatted")
FORMATTED_DIR.mkdir(parents=True, exist_ok=True)

# your fixed template string
TEMPLATE = """
## Proposed EC/sub-subclass:
2.7.11.22 

## Accepted name:
Cyclin-dependent kinase 1

## Synonyms:
Previously called cdc2 (S. pombe) and Cdc28 (S. cerevisiae). CDK1-cyclin B also called Maturation (or M-phase or Mitosis) promoting factor (MPF).

## Phylogeny:  
Essential function, conserved in metazoans and fungi. Single cell cycle kinase in yeast (Schizosaccharomyces pombe, Cdc2, Saccharomyces cerevisiae, Cdc28).

## Reaction catalysed:
ATP + L-seryl/threonyl-[protein] <=> ADP + H(+) + O-phospho-L-seryl/threonyl-[protein]

## Cofactor requirements: 
Mg++

## Specificity: 
In peptide arrays, CDK1 phosphorylates Ser or Thr residues, with a preference for Pro at +1 and a basic residue at +3 (PMID: 36631611). Threshold activities drive cell cycle transitions (PMID: 8855663) and bound accessory proteins (e.g. cyclin partner and Cks1) contribute to substrate recruitment and specific phosphorylation site selection (PMID: 36840943). +1 Pro preference is relaxed when the CDK1-cyclin-Cks1 complex is bound to a previously phosphorylated substrate through the Cks1 phospho- Thr/Ser binding site (PMID: 21816347, 19779198, 30640587).

## Structure:
CDK1 sequence encodes only the core protein kinase catalytic domain and CDK1 adopts an inactive fold in the absence of a cyclin partner (PMID: 25864384, PDB: 4YC6). Cyclin binding and phosphorylation on T161 within the activation segment are required for catalytic activity (PDB: 4YC3).

## Regulation: 
Requires cyclin binding for activity. Essential role characterised through genetic studies in yeasts (S. pombe (cdc2) and S. cerevisiae (Cdc28)) and physiological studies of clam, frog, sea urchin and starfish eggs and oocytes (PMID: 12045216, 7877684). Partners cyclins A and B in human cells. Activated by phosphorylation of the activation segment (equivalent to T161 in human CDK1) by monomeric CAK1 in S. cerevisiae and CDK7-cyclin H in other species (PMID: 10889219, EC 2.7.11.22).  Inhibited by phosphorylation within the glycine-rich loop (equivalent to Thr14 and Tyr15 in human CDK1) by membrane-associated tyrosine and threonine-specific cdc2-inhibitory kinase (Myt1) and by Wee1 protein kinase family members respectively. Activated by Cdc25 phosphatases.  When cyclin bound, can be inhibited by cyclin-dependent kinase inhibitor 1 (CDKN1A/B/C) family members in higher eukaryotes, also called p21 or Cip1 (CDKN1A), p27 or Kip1 (CDKN1B) and p57 or Kip2 (CDKN1C). In S. cerevisiae, inhibited by Far1 or Sic1 when bound to Cln (G1) or Clb5/6 (S phase) cyclins respectively, and in S. pombe inhibited by rum1 when bound to cig2 (G1/S) or cdc13 (G2/M) cyclins.

## Function:
Universal role in controlling entry into mitosis (PMID: 2138713).  CDK1 is the only essential cell cycle CDK in mammalian cells (PMID: 17700700). Phosphorylates diverse substrates that execute DNA segregation and cytokinesis.  

## Inhibitors:
CDK1-cyclin B- ATP-competitive inhibitor structures are available (PMIDs: 25864384 and 30472117 and PDB entries therein). A number of potent (Ki nM) ATP-competitive inhibitors are commercially available but all show significant activity against other members of the CDK family/ other protein kinases.  

DISCLAIMER: Several inhibitors are reportedly effective against this protein kinase; however, their specificity is never absolute, and even more selective and potent agents may become available. Resources that compare the efficacy of these and other compounds against a spectrum of protein kinases should be consulted,  including the Chemical Probes portal (https://www.chemicalprobes.org) supported by the Wellcome Trust, the MRC Kinase Inhibitor Database (www.kinase-screen.mrc.ac.uk/kinase-inhibitors), a resource curated by the NIH (https://pharos.nih.gov/), the protein kinase ontology database (http://prokino.uga.edu/), and the KLIFS (Kinase–Ligand Interaction Fingerprints and Structures) database (https://klifs.net).

## Other comments:
Aberrant high levels of cyclin B1 and B2 expression have been reported in various tumour types and can drive deregulated CDK1 activity (PMID: 33891890). Selective targeting of CDK1 for cancer treatment has not been extensively pursued given the essential nature of CDK1 activity in non-transformed cells.      

## References: 
See inline PMIDs
"""

# initialize the LLM client
llm = ChatOpenAI(
    model_name="o3",
    # temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def format_nomenclature(nomenclature: str, template: str) -> str:
    """
    Send the combined prompt to the LLM and return its formatted response.
    """
    system_msg = HumanMessage(content="You are a nomenclature formatting assistant.")
    user_msg   = HumanMessage(content=(
        "Summarize and reformat the structure and wording and tone of the following nomenclature "
        "to be similar to the template. DO NOT add new information or interpret the results. Only use the information provided in Nomenclature section below as the data source:\n\n"
        f"## Nomenclature:\n{nomenclature}\n\n"
        f"## Template:\n{template}"
    ))
    response = llm.invoke([system_msg, user_msg])
    return response.content

def sanitize_filename(name: str) -> str:
    """
    Remove any unsafe characters for filenames.
    """
    return "".join(c for c in name if c.isalnum() or c in " -_()").strip()

def main():
    for txt_path in INPUT_DIR.glob("*.txt"):
        protein_name = txt_path.stem
        safe_name    = sanitize_filename(protein_name)
        out_path     = FORMATTED_DIR / f"{safe_name}_formatted.txt"

        # if out_path.exists():
        #     print(f"✔ Skipping {txt_path.name}, formatted exists.")
        #     continue

        nomenclature = txt_path.read_text(encoding="utf-8")
        if not nomenclature.strip():
            continue

        try:
            formatted = format_nomenclature(nomenclature, TEMPLATE)
            out_path.write_text(formatted, encoding="utf-8")
            print(f"✔ Saved {out_path.name}")

                # Convert markdown to DOCX
            docx_path = out_path.with_name(out_path.stem + ".docx")
            pypandoc.convert_text(
                formatted,
                to="docx",
                format="md",
                outputfile=str(docx_path)
            )
            print(f"✔ Saved {docx_path.name}")
        except Exception as e:
            print(f"✖ Error processing {txt_path.name}: {e}")

if __name__ == "__main__":
    main()
