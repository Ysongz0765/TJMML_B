---
name: mcm-paper-visualization
description: Reproducible scientific visualization workflow for the TJMML_B mathematical-modeling paper. Use when generating, revising, auditing, or exporting Q1/Q2/Q3 figures from frozen CSV/XLSX/JSON or formal program outputs, especially radar charts, ranking-with-CI plots, heatmaps, slopegraphs, CES sensitivity plots, cost decompositions, Pareto panels, and LaTeX-ready PDF/SVG/PNG figures.
---

# MCM Paper Visualization

## Overview

Build every paper figure from traceable Q1/Q2/Q3 data sources under one low-saturation visual system. Preserve statistical meaning exactly: never rewrite frozen numbers, infer data from raster images, convert `NA` to zero, or fabricate bootstrap uncertainty.

## Non-Negotiable Data Rules

- Read from `frozen/`, formal `outputs/`, or explicitly documented Q2/Q3 interface files.
- Record the exact source path and source version for each figure.
- Keep structural `NA` distinct from observed zero. Use masked plotting or an explicit annotation.
- Use real bootstrap draws for confidence intervals and rank probabilities. Do not mix latent-theta SD with 0-100 score SD.
- Do not manually transcribe key statistics from screenshots or PDFs.
- Do not alter model results for visual symmetry, ranking appearance, or palette balance.
- Validate joins by stable `model_id`, scenario code, and dimension name before plotting.

## Visual System

- White background, generous margins, fine axes, pale grid lines, no 3D, no glow, no heavy borders.
- Use the project palette: mist blue `#8DB3D0`, cream `#E5DABC`, sage `#C0D7BE`, ice blue `#DCE9ED`.
- Extend the palette with same-family lightness, alpha, markers, line styles, and hatches rather than high-saturation colors.
- Prefer serif text for model names, numbers, and formulas; select an installed CJK fallback for Chinese labels.
- Export PDF and SVG for LaTeX, plus 300 dpi PNG for visual QA.
- Use the shared project module at `scripts/plotting/style.py` when it exists. The bundled skill scripts are thin, deterministic helpers.

## Figure Selection

- Choose a chart only when it answers a stated mathematical question.
- Q1: coverage matrix, missing-aware Spearman heatmap, five-dimensional radar plus Ranking-A score/95% CI panel, rank-probability heatmap, and compact LOFO/LOSO sensitivity.
- Q2: scenario demand matrix, three-panel CES utility dot/lollipop plot, Q1-to-scenario slopegraph or bump chart, and representative rho sensitivity.
- Q3: input/output cost decomposition, three-panel utility-cost Pareto plot, and workload-scale cost curves; include price perturbation only when it supports a stability claim.
- Avoid duplicate figures, Excel screenshots, decorative pie charts, crowded legends, and large tables rendered as images.

## Workflow

1. Identify the frozen or formal source and inspect headers, row counts, missingness, units, and join keys.
2. Write or update the data manifest before plotting.
3. Define the conclusion for the figure in one sentence.
4. Build the figure using the shared style and source data.
5. Export PDF/SVG/PNG with stable dimensions.
6. Run `validate_figure.py` and inspect the PNG or rendered PDF page.
7. Register the figure in `paper_audit.md` and cite it from the manuscript.

## Repository Integration

- Keep frozen directories read-only.
- Place integrated paper outputs under the new paper workspace and figures under its `figures/` directory.
- Use `scripts/plotting/q1_figures.py`, `q2_figures.py`, and `q3_figures.py` for paper figures; keep source-specific transformations explicit.
- Re-run the figure validator after LaTeX compilation and visually inspect the final PDF for clipping, unreadable labels, font substitution, float drift, and overfull boxes.

See `references/chart_selection.md`, `references/color_palette.md`, and `references/mcm_figure_style.md` for detailed decisions and QA checks.
