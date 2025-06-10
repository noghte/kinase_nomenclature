# Building an AI-Driven Kinase Nomenclature Pipeline

## Introduction & Motivation

### Why Kinase Nomenclature Matters
- Importance of consistent naming for protein kinases in research  
- Challenges: literature is dispersed, free-text descriptions vary, manual curation is laborious  
- Impact on downstream applications: databases, pathway analysis, drug design  

### High-Level Project Goals
- Automate extraction of EC numbers, names, synonyms, and functional annotations  
- Consolidate data from PDFs, databases, and web sources  
- Provide both textual reports and a browsable web interface  
- Design for extensibility: adding new sections or data sources should be straightforward  

## Approaches

- **FutureHouse**: fully automated  
- **Custom LLM agents**: semi-automated with human-in-the-loop  

## FutureHouse

### Robin Paper
- Explain the method and key contributions (15 minutes)

### Calling FutureHouse for Bulk Annotation
```bash
python futurehouse/futurehouse_submit_tasks.py \
  --input data/kinases_list.csv \
  --prompt futurehouse/unified_prompt.txt
```

- Display task status  
- Demonstrate fetching and formatting results  

### Ansley and Clark Example
- Explain an example of manual curation  
- Explain a FutureHouse output  
- Compare results and differences  

## Custom LLM Agents

### Motivations
- FutureHouse uses a single prompt for all tasks, which may not be optimal  
- FutureHouse cannot use custom PDF contexts (only free papers)  

### System Architecture Overview

#### End-to-End Pipeline Diagram
- Show Mermaid-based graph (`graph_visualization.png`)  
- Major stages: PDF loading → LLM agents → Document assembly → Web app  

#### Core Components
- **Backend (CLI Pipeline)**  
  - `main.py` orchestrates LangGraph  
  - `tools.py` defines LLM-based extractors  
  - `utils.py` handles PDF parsing and LLM setup  

- **Frontend (SvelteKit)**  
  - UI for querying and displaying results  
  - Connects to PostgreSQL  
  - Supports reviewer login and commenting  

### Data Flow & Extraction Logic

#### Loading & Parsing PDFs
- `load_pdf` uses PyMuPDF  
- Handles complex layouts by flattening pages into a blob  
- Example: `./pdf/DCLK1/`

#### LLM-Based Extraction Agents
- Invoked via LangChain’s tool interface  
- Agents include:
  - `extract_name_and_synonyms`  
  - `extract_gene_location`  
  - `extract_structure_info`  
  - `extract_regulation_info`  
  - `extract_function_info`  
  - `extract_specificity_info`  
  - `get_phylogeny`, `get_reaction_catalyzed`, `get_cofactor_requirements`, `get_inhibitors`, `get_db_links` (placeholders)

#### Prompt Templates & Customization
- Stored in `prompts/`  
- Each prompt file customizes behavior  
- Snippet from `name_and_synonyms.txt`  
- Templates update behavior without changing code  

#### Assembling the Final Report
- `assemble_doc` concatenates extracted sections  
- Output: Markdown-based `.txt` file  
- Example: `DCLK1_nomenclature.txt`

#### Bulk Annotation with FutureHouse
- Workflow:
  - `unified_prompt.txt`  
  - `futurehouse_submit_tasks.py`  
  - `futurehouse_fetch_responses.py`  
  - `futurehouse_format_answers.py`

#### tools.py Highlights
- Each `@tool` wraps an LLM call  
- Example:
```python
@tool
def extract_name_and_synonyms(protein_name: str, pdf_text: str) -> str:
    # Calls GPT-4 with prompt from prompts/name_and_synonyms.txt
```
- Emphasize modularity: add new tools and nodes easily  

#### main.py and LangGraph
- Uses `StateGraph(GraphState)`  
- Nodes = extraction steps  
- Edges = execution order  
- Entry: `load_context`, Exit: `assemble_doc`  
- LangGraph handles orchestration and visualization  

## Demonstration

### Live CLI Demo
- Place PDFs in `./pdf/<ProteinName>/`  
- Run:
```bash
python main.py \
  --protein-name DCLK1 \
  --pdf-path ./pdf/DCLK1/ \
  --output DCLK1_nomenclature.txt
```

- Output includes:
  - `graph_visualization.png`
  - Generated `.txt` report

### Web UI
- Enter kinase name in search bar  
- Displays nomenclature sections  
- Example: "DCLK1" query shows structured results  

### Database Schema (Optional)
- PostgreSQL Tables:
  - `kinases`: keyed by name/UniProt ID  
  - `synonyms`: many-to-one  
  - `inhibitors`, `cofactors`: JSON or normalized  

### Configuration Files & Environment Variables
- `.env`:  
  - `OPENAI_API_KEY`, `FUTUREHOUSE_API_KEY`  
- `webapp/.env`:  
  - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `JWT_SECRET`  
- Show sample (redacted) `.env` format  

## Evaluation & Future Directions

### Current Accuracy & Validation
- Compare LLM outputs to curated gold standard  
- Example:
  - “In pilot with 50 kinases, 92% EC number match”  
- Highlight metrics: precision, recall  

### Limitations & Challenges
- LLM hallucinations (e.g., fake synonyms)  
- Poor OCR on scanned PDFs  
- API rate limits, costs  

### Planned Enhancements
- Use structured APIs (e.g., UniProt XML, Reactome)  
- Add isoform/variant section via ClinVar, Ensembl  
- Better UI: filters for family, localization  
- Cache layer for repeated queries  
- Fine-tune small LLM on kinase corpus  

### Broader Applications
- Apply to other enzyme families (e.g., phosphatases)  
- Auto-update biological databases  
- Educational use: real-time kinase summaries  

## Q&A and Discussion

### Open Questions
- What metadata do researchers need most?  
- How to involve domain experts in improving prompts?