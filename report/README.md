# IEEE report

Report for the IEEE Research Paper Writing Workshop (14 November 2026): *Autonomous Healthcare-Waste Collection Robot: A Simulation-First System with Camera-Verified Container Handling*.

| File | What it is |
|---|---|
| `IEEE_Report.pdf` | The built report (IEEE conference format, 8 pages including references) |
| `main.tex`, `references.bib`, `figures/` | LaTeX source (`IEEEtran` conference class, BibTeX) |
| `data/runs_56_139.csv` | The run log. The tables use runs 56-128 (73 runs: 67 normal tasks, 6 staged faults); runs 129-139 are the later runs described in Section "Later runs and stress trials" |
| `scripts/analyze_runs.py` | Recomputes the numbers and the results figure from the run log |
| `scripts/plot_map_paper.py` | Draws the clinic map figure |

To build: upload the folder to Overleaf, or run `latexmk -pdf main.tex` (pdfLaTeX + BibTeX). If a citation shows `[?]`, build again.

## References

Every reference with a DOI was rebuilt from its Crossref record and links to `https://doi.org/<DOI>`. The web sources (WHO, WHO/UNICEF, Aethon, HFM Magazine, Diligent Robotics, Relay Robotics, TurtleBot 4 manual, Open-RMF, this repository) were opened and checked on 11 November 2026.
