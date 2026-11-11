# IEEE report

Report for the IEEE Research Paper Writing Workshop (14 November 2026): *Autonomous Healthcare-Waste Collection Robot: A Simulation-First System with Camera-Verified Container Handling*.

| File | What it is |
|---|---|
| `IEEE_Report.pdf` | The built report (IEEE conference format, 7 pages, clickable references) |
| `main.tex`, `references.bib`, `figures/` | LaTeX source (`IEEEtran` conference class, BibTeX) |
| `IEEE_Report_Overleaf.zip` | The same source as one zip, to upload to Overleaf |
| `data/runs_56_128.csv` | The run log used in the results (73 runs: 67 normal tasks, 6 staged faults) |
| `scripts/analyze_runs.py` | Recomputes every number and the results figure from the run log |
| `build.ps1` | Local build on Windows with MiKTeX (see below) |

## Open in Overleaf

Either upload `IEEE_Report_Overleaf.zip` (Overleaf: New Project, Upload Project), or open this link while signed in to Overleaf:

`https://www.overleaf.com/docs?snip_uri=https://raw.githubusercontent.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT/main/report/IEEE_Report_Overleaf.zip`

## Edit and see the PDF update (VS Code)

Open the `report` folder in VS Code (File, Open Folder) with the LaTeX Workshop extension. Save `main.tex` or `references.bib` and the PDF rebuilds by itself (pdfLaTeX, BibTeX, pdfLaTeX twice) and refreshes in the PDF tab. The helper files (`.aux`, `.bbl`, `.log` and similar) are deleted after every build, so only the `.tex`, `.bib` and `.pdf` files stay. The editor settings live in `report/.vscode/settings.json` on the reference laptop (they contain absolute paths, so they are not committed). In Overleaf, the same project compiles by itself on save.

If you see `[?]` where a citation number should be, the build stopped after the first pass: build again.

## Build locally (Windows, MiKTeX)

```
powershell -File build.ps1
```

On the reference laptop the `pdflatex` launcher of MiKTeX fails with a missing-DLL error, so `build.ps1` calls the engine directly (`miktex-pdftex -undump=pdflatex`) and then `miktex-bibtex`. On a normal installation `latexmk -pdf main.tex` works.

## References

Every reference with a DOI was rebuilt from its Crossref record (authors, venue, volume, pages) and links to `https://doi.org/<DOI>`. The web sources (WHO, WHO/UNICEF, Aethon, HFM Magazine, Diligent Robotics, Relay Robotics, TurtleBot 4 manual, Open-RMF, this repository) were opened and checked on 11 November 2026.
