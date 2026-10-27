## Personal CV
<div align="left">
  
  <a href="https://asantini29.github.io/myCV/resume_cv.pdf">
    <img alt="View CV (GitHub Pages)" src="https://img.shields.io/badge/View%20CV-GitHub%20Pages-blue.svg" />
  </a>
 
</div>

<br />
My Curriculum Vitae, available at: https://asantini29.github.io/myCV/resume_cv.pdf. 

Template forked from https://github.com/posquit0/Awesome-CV.

### Editing

Talks, outreach and education live in `data/*.yml` (each file lists its fields
at the top). The matching `cv/cv-sections/*.tex` files are generated from them
by `generate_sections.py`, which runs automatically in `build_cv.py` and in
every latexmk / LaTeX Workshop build, so edit the YAML, not the `.tex`.
The website (asantini29.github.io) reads the same files, plus `data/papers.yml`
for website-only paper extras. Requires PyYAML once: `pip install pyyaml`.
