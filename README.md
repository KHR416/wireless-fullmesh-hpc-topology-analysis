# Wireless Full-Mesh HPC Topology Thesis

This repository contains the cleaned thesis/poster handoff materials for the wireless full-mesh HPC datacenter topology analysis.

## Contents

- `paper/thesis_draft_en.tex`: LaTeX source for the current English manuscript.
- `paper/thesis_draft_en.pdf`: PDF built from the LaTeX source.
- `figures/`: figures referenced by the paper.
- `scripts/`: analytical plotting scripts for bisection-width and traffic-aware required-bandwidth curves.
- `results/topobench/`: compact CSV outputs copied from the TopoBench reproduction runs.

## Related Code Repository

TopoBench reproduction and modifications are intentionally kept in a separate repository:

```text
https://github.com/KHR416/topobench
```

That repository preserves the TopoBench commit history and makes the local modifications visible in git history.

## Build

```sh
cd paper
latexmk -pdf -interaction=nonstopmode thesis_draft_en.tex
```

The paper expects figures at `../figures/...`, so keep the directory layout unchanged.
