# ArXiv manuscript

`main.tex` is the submission source and `references.bib` contains the cited primary literature.

Build with:

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The manuscript deliberately distinguishes controlled simulation, online-defense model canaries, and offline sequential monitoring. It does not claim that autonomous stack-aware best response or a genuinely held-out model family has been executed.
