# Q3 Price Collection TODO

Pricing was not filled with formal values because the repository model names are exact future/specific configurations and their official API prices were not confirmed during framework setup.

Required verification sources:

- OpenAI: https://openai.com/api/pricing/
- Anthropic: https://docs.anthropic.com/en/docs/about-claude/pricing
- Google Gemini API: https://ai.google.dev/gemini-api/docs/pricing
- Moonshot / Kimi: https://platform.moonshot.cn/docs/pricing
- DeepSeek: https://api-docs.deepseek.com/quick_start/pricing
- Alibaba / Qwen / DashScope: https://help.aliyun.com/zh/model-studio/billing-for-model-studio
- Zhipu / GLM: https://docs.bigmodel.cn/cn/guide/models/price

Rules:

- Verify exact model/version/configuration against Q1/Q2 names.
- Record `price_date`.
- Use standard realtime API price, not batch or cached price, as the primary input/output price.
- Convert non-USD units to `USD / 1M tokens` and record conversion date/source in `notes`.
- Leave unknown values as `NA`; never infer prices from nearby model names.

