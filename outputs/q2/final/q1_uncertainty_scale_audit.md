# Q1 uncertainty scale audit

`Q1_UNCERTAINTY_SCALE_AUDIT = PASS`

## Evidence chain

- Q1 raw source: `C:\Users\1\Desktop\校赛B题\tmp\q2_git_import_754bc1b\TJMML_B-754bc1b541b5b0d27e8b74b75b979849edf72cda\outputs\q1_v1.2\bootstrap\bootstrap_bt_theta_v1.2.csv`
- Raw source SHA-256: `961d3d703d69532a5c6bf07948bc437f3e085fdc9d73d2a17f0d390794d24890`
- Raw fields: `bootstrap`, `dimension`, `model_id`, `theta`.
- Raw rows: 100000; bootstrap replicates: 2000.
- Q2 standardization code groups the raw `theta` column by `(model_id, dimension)` and writes its sample mean and sample SD to `theta_bootstrap_mean` and `theta_bootstrap_sd`.
- The separate `score_bootstrap_mean` and `score_bootstrap_sd` fields are computed from the 0-100 score replicate file and are not used in the latent-theta uncertainty equation.

## Numerical reconstruction

- Model-dimension groups checked: 50.
- Maximum absolute mean difference: 9.714e-17.
- Maximum absolute SD difference: 1.665e-16.
- Latent-theta SD range: [0.00374775, 0.109139].
- 0-100 score SD range: [2.45536, 49.6075].
- Structural-C5 groups with latent SD intentionally unavailable: 3.

## Conclusion

`theta_bootstrap_sd` is reconstructed directly from the raw Bradley-Terry `theta` bootstrap replicates and is in the same latent-theta scale as the point estimate used in Q2. No 0-100 score SD is added to latent theta. The existing uncertainty propagation equation is dimensionally valid and is retained.
