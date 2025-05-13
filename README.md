
# Kinase Nomenclature Generator using AI agents

Each section of the nomenclature will be handled by an independent node/agent.

## Agents

- Section:	Node Name	Prompting Strategy
- **EC Number / Name**:	`agent_name`	Extract EC number, accepted name, and synonyms
- **Phylogeny**	`agent_phylogeny`	Describe evolutionary history & orthologs
- **Species Info**	`agent_species`	Extract human/mouse gene location and expression
- **Reaction**	`agent_reaction`	Summarize catalyzed reaction + cofactor requirements
- **Specificity**	`agent_specificity`	Identify known substrates and their roles
- **Structure**	`agent_structure`	Parse domain organization and key residues
- **Regulation**	`agent_regulation`	Describe activation/inhibition and isoforms
- **Function**	`agent_function`	Detail developmental or pathological roles
- **Inhibitors**	`agent_inhibitors`	List known inhibitors and effects
- **Comments/Notes**	`agent_comments`	Miscellaneous info, domain-specific remarks
- **Databases**	`agent_databases`	Extract UniProt, KEGG, NCBI links etc.
- **References**	`agent_references`	Output clean list of cited references

Each agent will:
	•	Use a shared base prompt template (section_prompt) with the section title
	•	Receive full or partial PDF text as context depending on its need

