# Q2 data boundary

This directory is the only supported Q1-to-Q2 tabular boundary.

- `q1_input_template.csv`: minimal required header.
- `q1_final_input_template.csv`: required header plus optional rank and interval fields.
- `q1_final_metadata_template.json`: finalisation metadata template; it is intentionally not finalised.
- `mock_q1_input.csv` and `mock_q1_metadata.json`: anonymous synthetic development data. `MOCK_DATA_ONLY = TRUE`.

The CSV templates contain headers only. Field definitions, units, ranges, and validation rules are documented in `docs/q1_to_q2_interface.md`; no current Q1 intermediate values are copied here.
