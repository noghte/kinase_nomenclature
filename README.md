
# Kinase Nomenclature Generator

This project uses AI agents to automatically extract and summarize key nomenclature information for protein kinases from scientific PDF literature. Each section of the nomenclature document (e.g., EC number, name and synonyms; gene location; structure; regulation; function; specificity; phylogeny; reaction catalyzed; cofactor requirements; inhibitors; and database links) is handled by a dedicated agent (tool). The pipeline is defined as a directed state graph using LangGraph and LangChain, where each node invokes a GPT-4-powered tool to perform targeted extraction. The final output is a consolidated text document, and a visual representation of the pipeline is saved as a PNG.

## Installation

Ensure you have Python 3.11+ installed via Conda, then create and activate a Conda environment:

```bash
conda create -n env-agents python=3.11 -y
conda activate env-agents
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Set your OpenAI API key in a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

Place your target PDF files in a directory (e.g., `./pdf/DCLK1/`). Run the main script with:

```bash
python main.py \
  --protein-name DCLK1 \
  --pdf-path ./pdf/DCLK1/ \
  --output DCLK1_nomenclature.txt
```

This will:

- Compile the extraction pipeline.
- Generate a pipeline visualization at `graph_visualization.png`.
- Execute each agent (tool) in sequence to extract section data.
- Write the final consolidated document to the specified output file.

## Pipeline Components

The project defines the following tools (agents) in `tools.py`:

- `load_pdf(pdf_path: str) -> str`  
  Load and extract text from all PDF files in the specified path.  
- `extract_name_and_synonyms(protein_name: str, pdf_text: str) -> str`  
  Extract EC number, accepted name, and synonyms.  
- `extract_gene_location(protein_name: str, pdf_text: str) -> str`  
  Extract gene location, species, and expression patterns.  
- `extract_structure_info(protein_name: str, pdf_text: str) -> str`  
  Extract structural details (domains, motifs, binding sites).  
- `extract_regulation_info(protein_name: str, pdf_text: str) -> str`  
  Extract regulation mechanisms (phosphorylation, regulators).  
- `extract_function_info(protein_name: str, pdf_text: str) -> str`  
  Extract functional information (pathways, targets).  
- `extract_specificity_info(protein_name: str, pdf_text: str) -> str`  
  Extract substrate specificity details.  
- `get_phylogeny(protein_name: str) -> str`  
  (Placeholder) Return phylogenetic information.  
- `get_reaction_catalyzed(protein_name: str) -> str`  
  (Placeholder) Return reaction catalyzed by the protein.  
- `get_cofactor_requirements(protein_name: str) -> str`  
  (Placeholder) Return cofactor requirements.  
- `get_inhibitors(protein_name: str) -> str`  
  (Placeholder) Return known inhibitors.  
- `get_db_links(protein_name: str) -> str`  
  (Placeholder) Return database links (e.g., UniProt, KEGG).

## Extending the Pipeline

To add a new section:

1. Implement a new tool in `tools.py` with the `@tool` decorator.
2. Add a corresponding node in `main.py` using `graph.add_node(...)`.
3. Connect it into the pipeline with `graph.add_edge(...)`.
4. Update the `assemble_doc` function in `main.py` to include the new section in the final document.

