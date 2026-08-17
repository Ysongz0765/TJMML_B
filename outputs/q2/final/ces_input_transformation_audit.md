# CES input transformation audit

`CES_INPUT_AUDIT = PASS`

- Primary mapping: `z_ij = exp(theta_ij - max_i theta_ij)`, with a separate maximum in each dimension.
- Maximum reconstruction error: 0.000e+00.
- Ordering preserved within every estimable dimension: True.
- All formal CES inputs are finite: True.
- All formal CES inputs are strictly positive: True.
- Observed latent-theta span: 0.382943; no overflow or underflow risk was encountered.
- Score-floor sensitivity columns checked: z_score_floor_delta_0.100, z_score_floor_delta_0.150, z_score_floor_delta_0.200, z_score_floor_delta_0.250, z_score_floor_delta_0.300.
- Every score-floor input is finite and positive: True.
- Structural C5 rows retain raw latent NA and use the explicit availability anchor; they are not treated as latent observations.
- The delta sensitivity calls the same reference-scene evaluator as the main transform, so KL constraints, scene weights and reference rho are unchanged within each matching scene setting.
