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
In peptide arrays, CDK1 phosphorylates Ser or Thr residues, with a preference for Pro at +1 and a basic residue at +3 (Johnson et al., 2023). Threshold activities drive cell cycle transitions (Stern & Nurse, 1996) and bound accessory proteins (e.g. cyclin partner and Cks1) contribute to substrate recruitment and specific phosphorylation site selection (Al-Rawi et al., 2023). +1 Pro preference is relaxed when the CDK1-cyclin-Cks1 complex is bound to a previously phosphorylated substrate through the Cks1 phospho- Thr/Ser binding site (Holt et al., 2009; Örd & Loog, 2019; Pagliuca et al., 2011).

## Structure:
CDK1 sequence encodes only the core protein kinase catalytic domain and CDK1 adopts an inactive fold in the absence of a cyclin partner (Brown et al., 2015) (PDB: 4YC6). Cyclin binding and phosphorylation on T161 within the activation segment are required for catalytic activity (PDB: 4YC3). 

## Regulation: 
Requires cyclin binding for activity. Essential role characterised through genetic studies in yeasts (S. pombe (cdc2) and S. cerevisiae (Cdc28)) and physiological studies of clam, frog, sea urchin and starfish eggs and oocytes (Dorée & Hunt, 2002; Morgan, 1995). Partners cyclins A and B in human cells. Activated by phosphorylation of the activation segment (equivalent to T161 in human CDK1) by monomeric CAK1 in S. cerevisiae and CDK7-cyclin H in other species (Liu & Kipreos, 2000).  Inhibited by phosphorylation within the glycine-rich loop (equivalent to Thr14 and Tyr15 in human CDK1) by membrane-associated tyrosine and threonine-specific cdc2-inhibitory kinase (Myt1) and by Wee1 protein kinase family members respectively. Activated by Cdc25 phosphatases.  When cyclin bound, can be inhibited by cyclin-dependent kinase inhibitor 1 (CDKN1A/B/C) family members in higher eukaryotes, also called p21 or Cip1 (CDKN1A), p27 or Kip1 (CDKN1B) and p57 or Kip2 (CDKN1C). In S. cerevisiae, inhibited by Far1 or Sic1 when bound to Cln (G1) or Clb5/6 (S phase) cyclins respectively, and in S. pombe inhibited by rum1 when bound to cig2 (G1/S) or cdc13 (G2/M) cyclins.

## Function:
Universal role in controlling entry into mitosis (Nurse, 1990).  CDK1 is the only essential cell cycle CDK in mammalian cells (Santamaría et al., 2007). Phosphorylates diverse substrates that execute DNA segregation and cytokinesis.

## Inhibitors:
CDK1-cyclin B- ATP-competitive inhibitor structures are available (Brown et al., 2015; Wood et al., 2019). A number of potent (Ki nM) ATP-competitive inhibitors are commercially available but all show significant activity against other members of the CDK family/ other protein kinases.  

## Other comments:
Aberrant high levels of cyclin B1 and B2 expression have been reported in various tumour types and can drive deregulated CDK1 activity (Suski et al., 2021). Selective targeting of CDK1 for cancer treatment has not been extensively pursued given the essential nature of CDK1 activity in non-transformed cells.

## References: 
Al-Rawi, A., Kaye, E., Korolchuk, S., Endicott, J. A., & Ly, T. (2023). Cyclin A and Cks1 promote kinase consensus switching to non-proline-directed CDK1 phosphorylation. Cell reports, 42(3), 112139. https://doi.org/10.1016/j.celrep.2023.112139 

Brown, N. R., Korolchuk, S., Martin, M. P., Stanley, W. A., Moukhametzianov, R., Noble, M. E. M., & Endicott, J. A. (2015). CDK1 structures reveal conserved and unique features of the essential cell cycle CDK. Nature communications, 6, 6769. https://doi.org/10.1038/ncomms7769 

Dorée, M., & Hunt, T. (2002). From Cdc2 to Cdk1: when did the cell cycle kinase join its cyclin partner?. Journal of cell science, 115(Pt 12), 2461–2464. https://doi.org/10.1242/jcs.115.12.2461 

Holt, L. J., Tuch, B. B., Villén, J., Johnson, A. D., Gygi, S. P., & Morgan, D. O. (2009). Global analysis of Cdk1 substrate phosphorylation sites provides insights into evolution. Science (New York, N.Y.), 325(5948), 1682–1686. https://doi.org/10.1126/science.1172867 

Johnson, J. L., Yaron, T. M., Huntsman, E. M., Kerelsky, A., Song, J., Regev, A., Lin, T. Y., Liberatore, K., Cizin, D. M., Cohen, B. M., Vasan, N., Ma, Y., Krismer, K., Robles, J. T., van de Kooij, B., van Vlimmeren, A. E., Andrée-Busch, N., Käufer, N. F., Dorovkov, M. V., Ryazanov, A. G., … Cantley, L. C. (2023). An atlas of substrate specificities for the human serine/threonine kinome. Nature, 613(7945), 759–766. https://doi.org/10.1038/s41586-022-05575-3 

Liu, J., & Kipreos, E. T. (2000). Evolution of cyclin-dependent kinases (CDKs) and CDK-activating kinases (CAKs): differential conservation of CAKs in yeast and metazoa. Molecular biology and evolution, 17(7), 1061–1074. https://doi.org/10.1093/oxfordjournals.molbev.a026387 

Morgan D. O. (1995). Principles of CDK regulation. Nature, 374(6518), 131–134. https://doi.org/10.1038/374131a0 

Nurse P. (1990). Universal control mechanism regulating onset of M-phase. Nature, 344(6266), 503–508. https://doi.org/10.1038/344503a0 

Örd, M., & Loog, M. (2019). How the cell cycle clock ticks. Molecular biology of the cell, 30(2), 169–172. https://doi.org/10.1091/mbc.E18-05-0272 

Pagliuca, F. W., Collins, M. O., Lichawska, A., Zegerman, P., Choudhary, J. S., & Pines, J. (2011). Quantitative proteomics reveals the basis for the biochemical specificity of the cell-cycle machinery. Molecular cell, 43(3), 406–417. https://doi.org/10.1016/j.molcel.2011.05.031 

Santamaría, D., Barrière, C., Cerqueira, A., Hunt, S., Tardy, C., Newton, K., Cáceres, J. F., Dubus, P., Malumbres, M., & Barbacid, M. (2007). Cdk1 is sufficient to drive the mammalian cell cycle. Nature, 448(7155), 811–815. https://doi.org/10.1038/nature06046 

Stern, B., & Nurse, P. (1996). A quantitative model for the cdc2 control of S phase and mitosis in fission yeast. Trends in genetics : TIG, 12(9), 345–350.Suski, J. M., Braun, M., Strmiska, V., & Sicinski, P. (2021). Targeting cell-cycle machinery in cancer. Cancer cell, 39(6), 759–778. https://doi.org/10.1016/j.ccell.2021.03.010 

Wood, D. J., Korolchuk, S., Tatum, N. J., Wang, L. Z., Endicott, J. A., Noble, M. E. M., & Martin, M. P. (2019). Differences in the Conformational Energy Landscape of CDK1 and CDK2 Suggest a Mechanism for Achieving Selective CDK Inhibition. Cell chemical biology, 26(1), 121–130.e5. https://doi.org/10.1016/j.chembiol.2018.10.015 
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
        "Summarize and reformat the structure and wording and tone of the following nomenclature to be similar to the template. "
        "to be similar to the template. DO NOT add new information or interpret the results. Only use the information provided in Nomenclature section below as the data source:\n\n"
        f"## Nomenclature:\n{nomenclature}\n\n"
        f"## Template:\n{template}"
        "## Phylogeny"
        "Summarize and identify the phylogenetic context of the protein based on the provided Nomenclature focusing particularly on the Phylogeny section. "
        "## Reaction Catalyzed\n"
        "Summarize and mention the **chemical reaction** catalyzed by this kinase based on the provided Nomenclature focusing particularly on the Reaction Catalyze section. Include only the reaction catalyzed with ATP substrates and products from the provided Nomenclature.\n\n"
        "## Cofactor Requirements\n"
        "Include only cofactor requirement (e.g., Mg²⁺, Mn²⁺) based on the provided Nomenclature.\n\n"
        "## Substrate Specificity\n"
        "Summarize the substrate specificity of the protein based on the provided Nomenclature focusing particularly on the Substrate Specificity section.\n\n"
        "## Structure\n"
        "Summarize the 3D structure of the protein based on the provided Nomenclature.\n\n"
        "## Regulation\n"
        "Summarize regulatory mechanisms based on the provided Nomenclature focusing particularly on the Regulation section.\n\n"
        "## Function\n"
        "Summarize the biological roles of the protein based on the provided Nomenclature focusing particularly on the Function section. Include these information if they are available in the providided Nomenclature: Expression patterns (tissue or cell-specific), Upstream/downstream kinases, substrates and interacting partners, Role in signaling pathways  \n\n"
        "## Inhibitors\n"
        "If available: Summarize the Inhibitors section of the provided Nomenclature (it could be in the Other Comments).\n\n"
        "## Other Comments\n"
        "Summarize the Other Comments section of the provided Nomenclature. If Inhibitors are found in the provided Nomenclature, include them.\n\n"
        "## 9. References\n"
        "Include all the References used to create this nomenclature with APA 7th edition format, similar to the `Tempalte`.\n\n"
        "---\n"
        "# Output Guidelines\n"
        "- The Inhibitors section is optional. Only include this section if inhibitors are available in the Nomenclature (particularly in the Other Comments section).\n"
        "- Other than Inhibitors, use the exact section names (do not remove or add new sections)\n"
        "- Do **not** include speculative or inferred content\n"
        "- Include relevant in-text citations that are mentioned in the `Nomenclature`, even if it is summarized. The citation style should be similar to the `Template`. \n"
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
        if safe_name != "MAPK14":
            continue  # Skip if not MAPK14
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
            docx_path = out_path.with_name(out_path.stem + "_ref2.docx")
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
