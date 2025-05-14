import argparse
import os
import glob
import nest_asyncio
from typing import TypedDict
from typing_extensions import NotRequired

from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod
from tools import (
    load_pdf,
    extract_name_and_synonyms,
    extract_gene_location,
    extract_structure_info,
    extract_regulation_info,
    extract_function_info,
    extract_specificity_info,
    get_phylogeny,
    get_reaction_catalyzed,
    get_cofactor_requirements,
    get_inhibitors,
    get_db_links,
)

class GraphState(TypedDict):
    protein_name: str
    pdf_path: str
    pdf_text: str
    name_and_synonyms: NotRequired[str]
    gene_location: NotRequired[str]
    structure: NotRequired[str]
    regulation: NotRequired[str]
    function: NotRequired[str]
    specificity: NotRequired[str]
    phylogeny: NotRequired[str]
    reaction: NotRequired[str]
    cofactors: NotRequired[str]
    inhibitors: NotRequired[str]
    databases: NotRequired[str]
    document: NotRequired[str]

# Load initial context from all PDFs in directory
def load_context(state: GraphState) -> GraphState:
    pdf_dir = state["pdf_path"]
    pattern = os.path.join(pdf_dir, "*.pdf")
    texts = []
    for pdf_file in glob.glob(pattern):
        texts.append(load_pdf.invoke(pdf_file))
    combined = "\n".join(texts)

    return {**state, "pdf_text": combined}


# Assemble final document
def assemble_doc(state: GraphState) -> GraphState:
    parts = []
    parts.append("# EC Number, Name & Synonyms")
    parts.append(state.get("name_and_synonyms", ""))
    parts.append("# Gene Location")
    parts.append(state.get("gene_location", ""))
    parts.append("# Structure")
    parts.append(state.get("structure", ""))
    parts.append("# Regulation")
    parts.append(state.get("regulation", ""))
    parts.append("# Function")
    parts.append(state.get("function", ""))
    parts.append("# Specificity")
    parts.append(state.get("specificity", ""))
    parts.append("# Phylogeny")
    parts.append(state.get("phylogeny", ""))
    parts.append("# Reaction Catalyzed")
    parts.append(state.get("reaction", ""))
    parts.append("# Cofactor Requirements")
    parts.append(state.get("cofactors", ""))
    parts.append("# Inhibitors")
    parts.append(state.get("inhibitors", ""))
    parts.append("# Databases")
    parts.append(state.get("databases", ""))
    return {"document": "\n\n".join(parts)}


graph = StateGraph(GraphState)
# Nodes
graph.add_node("load_context", load_context)

graph.add_node(
    "extract_name_and_synonyms",
    lambda st: {
        "name_and_synonyms": extract_name_and_synonyms.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_gene_location",
    lambda st: {
        "gene_location": extract_gene_location.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_structure",
    lambda st: {
        "structure": extract_structure_info.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_regulation",
    lambda st: {
        "regulation": extract_regulation_info.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_function",
    lambda st: {
        "function": extract_function_info.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_specificity",
    lambda st: {
        "specificity": extract_specificity_info.invoke(
            {"protein_name": st["protein_name"], "pdf_text": st["pdf_text"]}
        )
    },
)

graph.add_node(
    "extract_phylogeny",
    lambda st: {"phylogeny": get_phylogeny(st["protein_name"])},
)

graph.add_node(
    "extract_reaction",
    lambda st: {"reaction": get_reaction_catalyzed(st["protein_name"])},
)

graph.add_node(
    "extract_cofactors",
    lambda st: {"cofactors": get_cofactor_requirements(st["protein_name"])},
)

graph.add_node(
    "extract_inhibitors",
    lambda st: {"inhibitors": get_inhibitors(st["protein_name"])},
)

graph.add_node(
    "extract_databases",
    lambda st: {"databases": get_db_links(st["protein_name"])},
)

graph.add_node("assemble_doc", assemble_doc)

# Edges
graph.set_entry_point("load_context")
graph.add_edge("load_context", "extract_name_and_synonyms")
graph.add_edge("extract_name_and_synonyms", "extract_gene_location")
graph.add_edge("extract_gene_location", "extract_structure")
graph.add_edge("extract_structure", "extract_regulation")
graph.add_edge("extract_regulation", "extract_function")
graph.add_edge("extract_function", "extract_specificity")
graph.add_edge("extract_specificity", "extract_phylogeny")
graph.add_edge("extract_phylogeny", "extract_reaction")
graph.add_edge("extract_reaction", "extract_cofactors")
graph.add_edge("extract_cofactors", "extract_inhibitors")
graph.add_edge("extract_inhibitors", "extract_databases")
graph.add_edge("extract_databases", "assemble_doc")
graph.add_edge("assemble_doc", END)


def main():
    # nest_asyncio.apply()
    parser = argparse.ArgumentParser()
    parser.add_argument("--protein-name", default="DCLK1")
    parser.add_argument("--pdf-path", default="./pdf/DCLK1/")
    parser.add_argument("--output", default="DCLK1_nomenclature.txt")
    args = parser.parse_args()

    # Compile and visualize graph
    app = graph.compile()
    graph_obj = app.get_graph()
    # print(graph_obj.draw_mermaid())
    png_data = graph_obj.draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
    with open("graph_visualization.png", "wb") as f:
        f.write(png_data)

    # Run pipeline
    iterator = app.stream(
        {"protein_name": args.protein_name, "pdf_path": args.pdf_path}
    )
    final_state = None
    for step in iterator:
        final_state = step
    result = final_state

    # Write document
    with open(args.output, "w") as fout:
        fout.write(result['assemble_doc']['document'])
    print(f"Document written to {args.output}")


if __name__ == "__main__":
    main()
