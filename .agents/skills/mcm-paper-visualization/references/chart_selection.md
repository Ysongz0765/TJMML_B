# Chart Selection

Start from the conclusion, then select the smallest chart that can support it.

| question | preferred chart | source contract |
| --- | --- | --- |
| Why is missing-aware estimation needed? | model x benchmark/setting coverage matrix | Q1 coverage table or frozen matrix |
| Are benchmark families redundant? | missing-aware Spearman heatmap | Q1 correlation output |
| What is the capability structure and overall result? | radar + horizontal score/CI panel | Q1 final dimension and Ranking-A outputs |
| How stable are ranks? | rank probability heatmap | real Q1 bootstrap rank draws |
| Does a source or family drive the result? | point-range or slope plot | Q1 LOFO/LOSO outputs |
| What does each scene require? | demand matrix | Q2 formal scene weights |
| Why do ranks move across scenes? | slopegraph/bump chart | Q1 Ranking-A rank and Q2 scene rank |
| Does CES substitution matter? | rho sensitivity lines | Q2 sensitivity output |
| Where does cost come from? | horizontal stacked bars | Q3 frozen scenario costs |
| What is the deployment trade-off? | three-panel utility-cost Pareto | Q3 frozen Pareto results |
| How does workload scale amplify cost gaps? | cost curves against `N_s` | Q3 frozen workload/sensitivity outputs |

Do not add a figure when it repeats an adjacent conclusion.
