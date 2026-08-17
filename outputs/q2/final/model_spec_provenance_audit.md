# Model specification provenance audit

`MODEL_SPEC_PROVENANCE_AUDIT = PASS`

| Field | Value |
|---|---|
| model_spec_sha256 | `5eb483577f32621802c3249d6a39fbdf81e8170fa6e1f7af2cf381fd3135482d` |
| model_spec_commit | `f30c5e41ff2cc0f92319dadab20b90c846ca40d3` |
| model_spec_commit_time | `2026-08-17T23:02:51+08:00` |
| final_run_time | `2026-08-17T23:10:28+08:00` |
| q1_data_commit | `754bc1b541b5b0d27e8b74b75b979849edf72cda` |
| q2_code_commit | `2d54b29879fe6ed65a9137c9cd8395baad825bbb` |
| snapshot_sha256 | `5eb483577f32621802c3249d6a39fbdf81e8170fa6e1f7af2cf381fd3135482d` |

The original untracked working-file history cannot prove that the specification preceded every exploratory calculation. The paper therefore uses the conservative statement that the specification was fixed and committed before this final clean rerun. For the frozen result reported here, the committed specification predates the run timestamp and its source, snapshot and metadata hashes are identical.
