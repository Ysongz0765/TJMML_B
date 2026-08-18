# Figure Style and QA

Use Matplotlib with stable dimensions, vector export, and a 300 dpi raster preview.

## Geometry

- Prefer single-column widths around 3.25 inches and two-column widths around 6.8 inches.
- Keep panel labels `(a)`, `(b)`, etc. outside the plotting data region.
- Use horizontal layouts for long model names.
- Reserve space for captions and legends; never allow a legend to cover data.

## Typography

- Use a serif family for numbers and model names.
- Detect a usable CJK font before plotting Chinese labels.
- Avoid text smaller than 7 pt in the final PDF.
- Keep model display names in one mapping table so figures and prose agree.

## Statistics

- Plot percentile confidence intervals from the actual bootstrap table when available.
- If only a formally defined score SD exists, document the conversion to `mean +/- 1.96 SD`.
- Never plot `theta` uncertainty as if it were score uncertainty.
- Mask structural `NA` values and annotate them in the caption or legend.

## Export and validation

Each figure should produce `.pdf`, `.svg`, and `.png`. Run the bundled validator to check:

- files exist and are non-empty;
- PNG dimensions meet the requested minimum;
- PDF/SVG files contain vector content;
- no `NA` values were silently converted to zeros;
- the figure manifest records the source and script.
