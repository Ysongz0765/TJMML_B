# Phase2 Coverage Optimization Report

## A. 数据覆盖
- 扩充前覆盖率: 36.15%
- 扩充后 Common Matrix 覆盖率: 74.21%
- 是否达到 70%: 是
- 若未达到，原因见 C3/事实性 Benchmark 的公开统一评测覆盖限制；本轮未为覆盖率降低可比性标准。

## B. 模型覆盖
```text
             model_id                               model  n_available  n_benchmarks  coverage_rate  number_of_capabilities_covered
          kimi_k3_max             Kimi K3 (max reasoning)           16            19       0.842105                               4
      gpt_5_6_sol_max                   GPT-5.6 Sol (max)           15            19       0.789474                               4
        gpt_5_5_xhigh                     GPT-5.5 (xhigh)           16            19       0.842105                               4
   claude_fable_5_max Claude Fable 5 (max, with fallback)           16            19       0.842105                               4
  claude_opus_4_8_max               Claude Opus 4.8 (max)           16            19       0.842105                               4
  gemini_3_1_pro_high               Gemini-3.1-Pro (High)           11            19       0.578947                               2
  deepseek_v4_pro_max                 DeepSeek-V4-Pro Max           14            19       0.736842                               3
deepseek_v4_flash_max               DeepSeek-V4-Flash Max           14            19       0.736842                               3
          qwen3_8_max                         Qwen3.8-Max           10            19       0.526316                               2
          glm_5_2_max                       GLM-5.2 (max)           13            19       0.684211                               2
```

## C. Benchmark 覆盖
```text
                                                         benchmark                           capability  coverage_rate evidence_role recommend_keep
                                   CorpusQA 1M [1M; ACC; tools=No]                      C3 Long context            0.2 VENDOR_REPORT         REVIEW
       FrontierSWE [Reported; Dominance score; tools=Agentharness]     C4 Code and software engineering            0.6 VENDOR_REPORT           TRUE
 GPQA Diamond [Diamond / OpenRouter fixed set; Accuracy; tools=No]                 C1 Complex reasoning            0.8   COMMON_EVAL           TRUE
                                 HLE-Full [Full; Pass@1; tools=No] C2 Knowledge and factual reliability            0.5 VENDOR_REPORT         REVIEW
            LiveBench AMPS_Hard [2026-06-25; Task score; tools=No]                 C1 Complex reasoning            1.0   COMMON_EVAL           TRUE
      LiveBench code_completion [2026-06-25; Task score; tools=No]     C4 Code and software engineering            1.0   COMMON_EVAL           TRUE
      LiveBench code_generation [2026-06-25; Task score; tools=No]     C4 Code and software engineering            1.0   COMMON_EVAL           TRUE
           LiveBench javascript [2026-06-25; Task score; tools=No]     C4 Code and software engineering            1.0   COMMON_EVAL           TRUE
LiveBench logic_with_navigation [2026-06-25; Task score; tools=No]                 C1 Complex reasoning            1.0   COMMON_EVAL           TRUE
            LiveBench math_comp [2026-06-25; Task score; tools=No]                 C1 Complex reasoning            1.0   COMMON_EVAL           TRUE
             LiveBench olympiad [2026-06-25; Task score; tools=No]                 C1 Complex reasoning            1.0   COMMON_EVAL           TRUE
               LiveBench python [2026-06-25; Task score; tools=No]     C4 Code and software engineering            1.0   COMMON_EVAL           TRUE
           LiveBench typescript [2026-06-25; Task score; tools=No]     C4 Code and software engineering            1.0   COMMON_EVAL           TRUE
         LiveBench zebra_puzzle [2026-06-25; Task score; tools=No]                 C1 Complex reasoning            1.0   COMMON_EVAL           TRUE
                           MMMU-Pro [Reported; Accuracy; tools=No]                        C5 Multimodal            0.5 VENDOR_REPORT         REVIEW
                                       MRCR 1M [1M; MMR; tools=No]                      C3 Long context            0.2 VENDOR_REPORT         REVIEW
                         MathVision [Reported; Accuracy; tools=No]                        C5 Multimodal            0.5 VENDOR_REPORT         REVIEW
             ProgramBench [Reported; Accuracy; tools=Agentharness]     C4 Code and software engineering            0.6 VENDOR_REPORT           TRUE
              SWE Verified [Verified; Resolved; tools=Agent_tools]     C4 Code and software engineering            0.2 VENDOR_REPORT         REVIEW
```

## D. 能力维度网络
```text
                          capability  connected_components                                                                                                                                                            isolated_models  graph_density connectivity_status
                C1 Complex reasoning                     1                                                                                                                                                                                  1.000000           CONNECTED
C2 Knowledge and factual reliability                     6                                                                              DeepSeek-V4-Flash Max; DeepSeek-V4-Pro Max; GLM-5.2 (max); Gemini-3.1-Pro (High); Qwen3.8-Max       0.222222        DISCONNECTED
                     C3 Long context                     9 Claude Fable 5 (max, with fallback); Claude Opus 4.8 (max); GLM-5.2 (max); GPT-5.5 (xhigh); GPT-5.6 Sol (max); Gemini-3.1-Pro (High); Kimi K3 (max reasoning); Qwen3.8-Max       0.022222        DISCONNECTED
    C4 Code and software engineering                     1                                                                                                                                                                                  1.000000           CONNECTED
                       C5 Multimodal                     6                                                                              DeepSeek-V4-Flash Max; DeepSeek-V4-Pro Max; GLM-5.2 (max); Gemini-3.1-Pro (High); Qwen3.8-Max       0.222222        DISCONNECTED
```

## E. 新数据来源
```text
source_id           publisher       evidence_role source_quality  new_valid_cells  new_models_connected  new_model_pairs_connected                    reduction_in_components  coverage_increase      protocol_consistency marginal_information_gain                                                                                                                                                          notes
   SRC006           LiveBench         COMMON_EVAL              A              100                    10                         45                    See network diagnostics             0.3806                      High                      High                                                       Official release CSV mirrored by LiveBench; individual task columns used, not a composite overall index.
   SRC007          OpenRouter         COMMON_EVAL              C                8                     8                         28                    See network diagnostics             0.3806                      High                      High Platform states it runs the same fixed question set across provider endpoints; GPT-5.6 Sol Pro was not mapped to GPT-5.6 Sol max because version names differ.
   SRC008             BenchLM       SUPPLEMENTARY              C                0                     0                          0 0; registered for metadata/validation only             0.0000 Not used in Common Matrix                       Low                                                         Used for metadata and source triangulation only; official LiveBench CSV is the primary numeric source.
   SRC009 Artificial Analysis EXTERNAL_VALIDATION              C                0                     0                          0 0; registered for metadata/validation only             0.0000 Not used in Common Matrix                       Low                                Composite index source registered for validation only; no composite score inserted into Common Matrix to avoid double counting.
   SRC001         Moonshot AI       VENDOR_REPORT              B               27                     6                         15                    See network diagnostics             0.0000                      High                    Medium                          Some non-Kimi scores are cited from external leaderboards or vendor reports within README; manual source-by-source audit recommended.
   SRC003            DeepSeek       VENDOR_REPORT              B                6                     2                          1                    See network diagnostics             0.0000                      High                    Medium                                                                                         Tables 23 and 24 were parsed with pandas.read_html from local archive.
```

## F. 数据质量
- Grade counts: {'Grade A': 100, 'Grade B': 91, 'Grade C': 18}
- Common Matrix Grade A/B ratio: 100.00%
- CrossValidationRate: 0.0000
- Human verification priority records: see `human_verification_priority.xlsx`.

## G. 是否可以进入正式建模
`NOT_READY`

前三项阻碍：C3 长上下文网络稀疏且不连通；C2 事实可靠性独立统一来源不足；C5 多模态主要依赖厂商表，无法连接 DeepSeek/Gemini/Qwen/GLM。