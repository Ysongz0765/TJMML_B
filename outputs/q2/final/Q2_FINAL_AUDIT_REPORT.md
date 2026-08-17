# Q2 final audit report

## Data

- Q1 freeze version: `frozen/v1.0 + Q1 v1.2 official outputs`
- Q1 data commit: `754bc1b541b5b0d27e8b74b75b979849edf72cda`
- Q2 code commit: `2d54b29879fe6ed65a9137c9cd8395baad825bbb`
- Q2 freeze version: `Q2_FINAL_v1.0`
- Q2 model-spec SHA-256: `5eb483577f32621802c3249d6a39fbdf81e8170fa6e1f7af2cf381fd3135482d`

## Audit

- uncertainty scale: PASS
- model spec provenance: PASS
- CES input transform: PASS
- scene definition: PASS
- structural C5: PASS
- PRI: PASS
- rank migration: PASS
- paper language: PASS
- PDF visual QA: PASS

## Results

- research: 1. Claude Fable 5 (max, with fallback) (0.918337); 2. Kimi K3 (max reasoning) (0.901293); 3. GPT-5.6 Sol (max) (0.899241)
- dialogue: 1. Claude Fable 5 (max, with fallback) (0.932419); 2. GPT-5.6 Sol (max) (0.932145); 3. Kimi K3 (max reasoning) (0.868707)
- coding: 1. Kimi K3 (max reasoning) (0.981302); 2. Claude Fable 5 (max, with fallback) (0.976204); 3. DeepSeek-V4-Pro Max (0.961063)

### Kimi K3

- research: rank 2; Top3 probability 0.7505.
- dialogue: rank 3; Top3 probability 0.4955.
- coding: rank 1; Top3 probability 0.9475.

## Robustness

- alpha-rho: 9 x 13 = 117 settings per scene and prior, with KL re-solved at every alpha.
- prior: Q1 objective prior and equal prior rerun from the frozen scene constraints.
- input transform: BT latent strength primary plus delta=0.10-0.30 positive-floor sensitivity.
- uncertainty: 2000 draws using audited latent-theta SD, seed 20260817.
- C5: anchor 0.20-0.50 sensitivity plus C1-C3 common-dimension dialogue rerun.

## Artifacts

- `sections/q2_final.tex`
- `paper/q2_standalone.tex`
- `output/pdf/Q2_Final_Paper.pdf`
- `outputs/q2/final/q2_freeze_manifest.csv`
- `q2/q3_handoff/q2_to_q3_scene_utility.csv`

`Q2_READY_TO_FREEZE = TRUE`
`Q2_READY_FOR_PAPER_MERGE = TRUE`
`Q2_READY_FOR_Q3_HANDOFF = TRUE`
