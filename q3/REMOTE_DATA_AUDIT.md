# Q3 Remote Data Audit

Audit date: 2026-08-17

## Remote References

| Remote ref | Latest commit | Date | Purpose | Q3 relevance |
|---|---|---|---|---|
| `origin/main` | `4cf90196c374f6ff16e874cde9929cec521fd6f1` | 2026-08-17 | Add the Q2 KL-CES scenario evaluation framework | Supplies the Q2 framework that Q3 consumes. |
| `origin/q2-data-prep` | `754bc1b541b5b0d27e8b74b75b979849edf72cda` | 2026-08-17 | Prepare standardized Q1 outputs for Q2 modeling | Provides the Q1-to-Q2 standardized data preparation. |
| `origin/q2-final-paper` | `bff0e185510f79bd78dd190ccedc47c81b12f137` | 2026-08-17 | Merge the audited Q2 data preparation into the final Q2 handoff | This is the frozen source for the formal Q2 utility interface. |
| `origin/q3-cost-pareto` | `6c459caeaaa6c2ebc1af23eb4550623200aa0fe8` | 2026-08-17 | Update Q3 pricing readiness checks | Base branch containing the Q3 framework and pricing audit. |

## Synchronization Record

Before synchronization, the local Q3 worktree had the Q2 interface templates but
did not contain the formal `scenario_utility.csv`,
`scenario_utility_bootstrap.csv`, `scenario_utility_summary.csv`, or
`q2_to_q3_validation.csv` files. The corresponding Q2 files were present in
`origin/q2-final-paper` and were copied into `q3/data/` without modification.
The interface document was copied from `q2/metadata/`.

Source branch: `origin/q2-final-paper`  
Source commit: `bff0e185510f79bd78dd190ccedc47c81b12f137`  
Synchronization date: `2026-08-17`

## SHA-256 Provenance

| Source path | Target path | SHA-256 |
|---|---|---|
| `q2/outputs/scenario_utility.csv` | `q3/data/scenario_utility.csv` | `82bc63f0d1983775bf9a512ad8e50d011c0d556cbdd56329ed8f74267de84ca1` |
| `q2/outputs/scenario_utility_bootstrap.csv` | `q3/data/scenario_utility_bootstrap.csv` | `1eea0558c3df5e46c9b3135a7810f4ef6dbb2258f96e4bef4ae4e84e8c64b323` |
| `q2/outputs/scenario_utility_summary.csv` | `q3/data/scenario_utility_summary.csv` | `5ff7d3311920b8f752729b5e26c1ccb315bf5c795a7c7fb39e9c132b808ba110` |
| `q2/outputs/q2_to_q3_validation.csv` | `q3/data/q2_to_q3_validation.csv` | `714c493d930dcf6d7c75d7f9b928a70ed40fd71077a1e48f402ae41d5ea8ef42` |
| `q2/metadata/q2_to_q3_interface.md` | `q3/data/q2_to_q3_interface.md` | `a86c57c77222632d6fed8362b725aea8d69b5852fa63c800eac5c087736056a5` |

The complete machine-readable record is
`q3/data/q2_interface_provenance.json`, which also stores target hashes.

## Validation

The nominal interface has 30 rows, 10 models, and 3 scenarios. The bootstrap
interface has 60,000 rows from 2,000 bootstrap draws. The synchronized
Q2-to-Q3 validation file reports 18/18 checks passed. Q3 independently
rechecked row counts, model identifiers, scenario coverage, duplicate keys,
missing utility values, and utility direction before running.
