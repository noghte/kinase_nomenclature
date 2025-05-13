from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from tools import (load_pdf, answer_question, extract_name_and_synonyms,
                   extract_gene_location, extract_structure_info,
                   extract_regulation_info, extract_function_info,
                   extract_specificity_info, get_phylogeny,
                   get_reaction_catalyzed, get_cofactor_requirements,
                   get_inhibitors, get_db_links)
from utils import Section

# Define graph state
type GraphState = dict[str, str]

# Define tool executor
tool_executor = ToolExecutor([
    extract_name_and_synonyms,
    extract_gene_location,
    extract_structure_info,
    extract_regulation_info,
    extract_function_info,
    extract_specificity_info
])

# Define core graph functions
def load_context(state: GraphState):
    protein_name = state["protein_name"]
    text = load_pdf(protein_name)
    return {"protein_name": protein_name, "text": text}

def run_tool(state: GraphState, tool_name: str):
    return tool_executor.invoke(
        ToolInvocation(tool_name=tool_name, input=state)
    )

# Define graph
graph = StateGraph(GraphState)
graph.add_node("load_context", load_context)
graph.add_node("name_and_synonyms", lambda state: run_tool(state, "extract_name_and_synonyms"))
graph.add_node("gene_location", lambda state: run_tool(state, "extract_gene_location"))
graph.add_node("structure", lambda state: run_tool(state, "extract_structure_info"))
graph.add_node("regulation", lambda state: run_tool(state, "extract_regulation_info"))
graph.add_node("function", lambda state: run_tool(state, "extract_function_info"))
graph.add_node("specificity", lambda state: run_tool(state, "extract_specificity_info"))

# Simple python functions
graph.add_node("phylogeny", lambda state: {"phylogeny": get_phylogeny(state["protein_name"])})
graph.add_node("reaction_catalyzed", lambda state: {"reaction": get_reaction_catalyzed(state["protein_name"])})
graph.add_node("cofactors", lambda state: {"cofactors": get_cofactor_requirements(state["protein_name"])})
graph.add_node("inhibitors", lambda state: {"inhibitors": get_inhibitors(state["protein_name"])})
graph.add_node("databases", lambda state: {"databases": get_db_links(state["protein_name"])})

# Edges
graph.set_entry_point("load_context")
graph.add_edge("load_context", "name_and_synonyms")
graph.add_edge("name_and_synonyms", "gene_location")
graph.add_edge("gene_location", "structure")
graph.add_edge("structure", "regulation")
graph.add_edge("regulation", "function")
graph.add_edge("function", "specificity")
graph.add_edge("specificity", "phylogeny")
graph.add_edge("phylogeny", "reaction_catalyzed")
graph.add_edge("reaction_catalyzed", "cofactors")
graph.add_edge("cofactors", "inhibitors")
graph.add_edge("inhibitors", "databases")
graph.add_edge("databases", END)

# Compile app
app = graph.compile()
