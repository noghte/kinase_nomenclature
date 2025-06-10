
# Kinase Nomenclature Generator

## Overview

The **Kinase Nomenclature Generator** is a modular, AI-driven pipeline that automatically extracts, consolidates, and formats comprehensive nomenclature and functional data for protein kinases from scientific literature and databases. Leveraging GPT-4-powered agents orchestrated by LangGraph and LangChain, the pipeline processes PDF sources, enriches metadata, and produces both textual reports and a visual pipeline graph. Additionally, the project provides utilities for data enrichment, bulk annotation workflows via FutureHouse, and a SvelteKit-based web application for browsing results.

## Features

- **Automated PDF Parsing**: Extract raw text from kinase-specific PDF documents.
- **LLM-based Extraction Agents**: Dedicated tools for extracting EC numbers, names/synonyms, gene location, structure, regulation, function, specificity, phylogeny, catalytic reaction, cofactors, inhibitors, and database links.
- **Pipeline Visualization**: Generate a Mermaid-based graph visualization of the extraction workflow.
- **Configurable Prompt Templates**: Customize extraction prompts in `prompts/`.
- **Bulk Annotation Workflow**: Submit and retrieve annotator tasks using FutureHouse (`futurehouse/`).
- **Data Enrichment Utilities**: Map gene symbols to UniProt IDs and integrate Excel data via helper scripts (`scripts/`).
- **Svelte Web Application**: Interactive UI for querying and exploring kinase nomenclature data.
- **Extensible Architecture**: Easily add new extraction sections or modify existing ones.

## Table of Contents

1. [Installation](#installation)
2. [Quickstart](#quickstart)
3. [Directory Structure](#directory-structure)
4. [Pipeline Components](#pipeline-components)
5. [Prompt Templates](#prompt-templates)
6. [Data Enrichment Scripts](#data-enrichment-scripts)
7. [FutureHouse Bulk Workflow](#futurehouse-bulk-workflow)
8. [Web Application](#web-application)
9. [Configuration](#configuration)
10. [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.11+ (via Conda recommended)
- Node.js 18+ and npm (for the web application)
- A PostgreSQL database (for the web application)

### Backend (CLI Pipeline)

1. Clone the repository and enter the directory:

   ```bash
   git clone <repo-url>
   cd kinase_nomenclature
   ```

2. Create and activate a Conda environment:

   ```bash
   conda create -n kinase-nomenclature python=3.11 -y
   conda activate kinase-nomenclature
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (create a root `.env` file):

   ```text
   OPENAI_API_KEY=<your-openai-key>
   FUTUREHOUSE_API_KEY=<your-futurehouse-key>
   ```

### Frontend (Web Application)

```bash
cd webapp
npm install
```

## Quickstart

### Generate a Nomenclature Report

Place your PDF files under `./pdf/<ProteinName>/` and run:

```bash
python main.py \
  --protein-name DCLK1 \
  --pdf-path ./pdf/DCLK1/ \
  --output DCLK1_nomenclature.txt
```

- **graph_visualization.png**: Pipeline graph output.
- **DCLK1_nomenclature.txt**: Consolidated report.

## Directory Structure

```text
.  
├── main.py                     # Orchestrates the LangGraph pipeline
├── tools.py                    # LLM-based extraction tool definitions
├── utils.py                    # LLM client setup & PDF extraction utilities
├── prompts/                    # Prompt templates for each extraction section
│   ├── name_and_synonyms.txt
│   ├── gene_location.txt
│   └── ...
├── scripts/                    # Data enrichment scripts (UniProt, Excel)
│   ├── extract_uniprots.py
│   ├── uniprot_to_excel.py
│   └── ...
├── futurehouse/                # Bulk annotation workflow via FutureHouse API
│   ├── unified_prompt.txt
│   ├── futurehouse_submit_tasks.py
│   ├── futurehouse_fetch_responses.py
│   ├── futurehouse_format_answers.py
│   └── futurehouse_api_test.py
├── webapp/                     # SvelteKit frontend application
│   └── ...
├── data/                       # Source data (kinases list, Excel, JSON)
│   └── ...
├── pdf/                        # Input PDFs per protein
│   └── DCLK1/
├── graph_visualization.png     # Pipeline visualization
├── requirements.txt
└── README.md
```

## Pipeline Components

The extraction pipeline (`main.py`) consists of LangChain tools (`tools.py`) that perform targeted LLM extractions:

| Tool                             | Description                                                  |
|----------------------------------|--------------------------------------------------------------|
| `load_pdf(pdf_path: str)`        | Extract raw text from PDF files                              |
| `extract_name_and_synonyms(...)` | EC number, accepted name, and synonyms                        |
| `extract_gene_location(...)`     | Gene location, species, and expression patterns               |
| `extract_structure_info(...)`    | Domain organization, binding sites, key motifs                |
| `extract_regulation_info(...)`   | Phosphorylation, regulators, activation/inhibition mechanisms |
| `extract_function_info(...)`     | Biological roles, pathways, targets                           |
| `extract_specificity_info(...)`  | Consensus substrate motifs                                    |
| `get_phylogeny(...)`             | Kinome group/family/subfamily assignment (placeholder)        |
| `get_reaction_catalyzed(...)`    | Catalytic reaction equation (placeholder)                     |
| `get_cofactor_requirements(...)` | Metal/cofactor dependencies (placeholder)                     |
| `get_inhibitors(...)`            | Known inhibitors (placeholder)                                |
| `get_db_links(...)`              | Database cross‐references (placeholder)                       |

The `assemble_doc` function concatenates each section under Markdown headers.

## Prompt Templates

Edit the system prompts for each section in `prompts/` to customize LLM extraction behavior.

## Data Enrichment Scripts

Helper scripts in `scripts/` map gene symbols to UniProt IDs and integrate results into Excel:

- `extract_uniprots.py`: Query UniProt API → `data/gene_to_uniprot.json`.
- `uniprot_to_excel.py`: Insert UniProt IDs into the master Excel workbook.
- `highlight_excel_file.py`: Highlight matched UniProt rows in Excel.
- `kinase_from_uniprot.py`: Enrich kinase metadata (names, synonyms, function).

## FutureHouse Bulk Workflow

1. **Template**: `futurehouse/unified_prompt.txt` defines the unified prompt.
2. **Submit Tasks**: `futurehouse/futurehouse_submit_tasks.py` → submit gene tasks.
3. **Fetch Responses**: `futurehouse/futurehouse_fetch_responses.py` → poll completed answers.
4. **Format Answers**: `futurehouse/futurehouse_format_answers.py` → convert MD → DOCX.
5. **API Test**: `futurehouse/futurehouse_api_test.py` → local task testing.

## Web Application

A SvelteKit front end for browsing kinase nomenclature:

```bash
cd webapp
npm run dev
```

Configure database connection via `webapp/.env`:

```text
DB_HOST=<host>
DB_PORT=<port>
DB_USER=<user>
DB_PASSWORD=<password>
DB_NAME=<dbname>
JWT_SECRET=<secret>
```

Build & preview:

```bash
npm run build
npm run preview
```

## Configuration

Environment variables are loaded from `.env` files:

- Root `.env`: `OPENAI_API_KEY`, `FUTUREHOUSE_API_KEY`
- `webapp/.env`: PostgreSQL + JWT settings

## Contributing

To extend the pipeline or add new sections:

- Define new `@tool` in `tools.py`.
- Add corresponding nodes/edges in `main.py`.
- Update prompt templates under `prompts/`.

---    

