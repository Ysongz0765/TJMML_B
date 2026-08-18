# Paper Audit v3

## Overall gate

**PASS: final-paper gate.**

The current artifact is `paper_final/final_paper_v3.pdf`. It was compiled
from `paper_final/main.tex` after the final language cleanup. Frozen Q1--Q3
data and formal numerical results were not changed.

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Original-problem audit | PASS with source limitation recorded | `contest_problem_mapping.md`; supplied PDF text layer has missing Adobe-GB1 mappings |
| Q1 mapping | PASS | Missing-aware five-dimensional evaluation, Ranking A, Bootstrap, LOFO |
| Q2 mapping | PASS | KL-projected scene weights, CES utility, scene ranking and migration |
| Q3 mapping | PASS | Workload cost, strict Pareto set, and budget decision intervals |
| Frozen-data protection | PASS | `git diff --name-only -- frozen` is empty |
| Figure style source | PASS | `scripts/plotting/style.py` exposes `PALETTE`, `MODEL_STYLE`, `STATUS_STYLE` |
| Figure artifact validation | PASS | `python scripts/plotting/validate.py paper_final/figures` validated 15 figure stems |
| Figure-text consistency | PASS | Captions and surrounding paragraphs describe the current figure forms |
| Language audit | PASS | `language_audit_v3.md` |
| Visual PDF audit | PASS | 18-page render set in `paper_final/rendered_v3_final/` |
| LaTeX build | PASS | Two consecutive XeLaTeX runs completed successfully |

## Formal result checks

- Q1 coverage: \(164/210=78.1\%\).
- Ranking A point-estimate top three: GPT-5.6 Sol, Claude Fable 5,
  Kimi K3.
- Kimi K3 Bootstrap Top-3 empirical probability: \(0.4225\).
- Research scene: Claude Fable 5 first; Kimi K3 second; GPT-5.6 Sol third.
- Coding scene: Kimi K3 first with formal utility \(0.9813\).
- Coding budget thresholds: \(0.01056\), \(0.03168\), and \(0.10683\) USD,
  switching through DeepSeek-V4-Flash, DeepSeek-V4-Pro, and Kimi K3.
- Strict Pareto excludes Claude Fable 5 because its fallback billing trace is
  incomplete, and GLM-5.2 because verifiable public input/output prices are
  unavailable.

## Build and visual notes

- Output PDF: 18 pages.
- Final PDF copy: `paper_final/final_paper_v3.pdf`.
- Rendered pages: `paper_final/rendered_v3_final/page-01.png` through
  `page-18.png`.
- The final render shows no clipped main figure, blank image, or stale figure
  description.
- Non-blocking warnings remain for underfull boxes in references and long
  price-configuration rows. They do not alter the mathematical content or
  page usability.

## Final deliverables

1. `final_paper_v3.pdf`
2. `contest_problem_mapping.md`
3. `figure_audit_v3.md`
4. `language_audit_v3.md`
5. `paper_audit_v3.md`

