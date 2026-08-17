# Scene definition audit

`SCENE_DEFINITION_AUDIT = PASS`

| Scene | Frozen CES core | Active KL dimensions | Grid |
|---|---|---|---:|
| Research | C1, C2, C3 | C1, C2, C3 | 9 x 13 |
| Dialogue | C1, C2, C3, C5 | C1, C2, C3, C5 | 9 x 13 |
| Coding | C1, C4 | C1, C4 | 9 x 13 |

The YAML specification, KL active-weight output, CES score implementation and paper table use the same sets. Non-core dimensions receive zero reported scene weight and are not passed to CES, so negative rho cannot penalize a non-core ability. Each scene-prior block contains 117 parameter settings x 10 models = 1170 rows.
