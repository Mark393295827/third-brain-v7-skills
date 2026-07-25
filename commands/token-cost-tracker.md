---
name: token-cost-tracker
description: Estimate, log, and report token usage using runtime-supplied billing rates; never rely on embedded model prices.
usage: "token-cost-tracker [estimate|log|report] [options]"
---

# Token Cost Tracker

This is a utility command, not an Agent Skill. Pricing and model catalogs change; obtain rates from the current runtime/provider billing source and record its timestamp.

## Inputs

```yaml
task: ""
model_id: "runtime identifier"
capability_class: fast | reasoning | multimodal | evaluator | other
input_tokens: 0
cached_input_tokens: 0
output_tokens: 0
rates_per_million:
  input: null
  cached_input: null
  output: null
currency: ""
rate_source: ""
rate_checked_at: ""
```

If rates are unavailable, return token totals and `cost_status: unknown`; do not guess a price.

## Estimate

Use measured source size, a comparable prior run, or an explicit low/base/high token range. Calculate each scenario:

```text
cost = (input_tokens / 1,000,000 * input_rate)
     + (cached_input_tokens / 1,000,000 * cached_input_rate)
     + (output_tokens / 1,000,000 * output_rate)
```

Report assumptions, rate source/age, and the budget stop threshold. Do not infer token count from pages without labeling the conversion assumption.

## Log

Append actual usage to `.token-log.csv`:

```csv
date,task,model_id,capability_class,input_tokens,cached_input_tokens,output_tokens,input_rate,cached_input_rate,output_rate,currency,cost,rate_source,notes
2026-07-11,wiki-ingest,runtime-model,reasoning,45231,12000,8732,0,0,0,USD,,provider-billing-page,rate unavailable at log time
```

Never rewrite historical rates. A later reconciliation appends a correction row referencing the original record.

## Report

For the requested period return:

- input, cached-input, output, and total tokens;
- known cost by currency (never combine currencies silently);
- unknown-cost rows requiring reconciliation;
- breakdown by task, capability class, and model id;
- estimate-versus-actual error when estimates exist;
- largest cost driver and one bounded optimization test.

## Failure Rules

- Missing token counts: return `NEEDS_INPUT`.
- Missing rates: compute usage only and mark cost unknown.
- Stale rates: use only when the user accepts the dated estimate; otherwise refresh.
- Mixed currencies: report separately or convert with an explicit dated exchange rate.
- Log path not writable: return `BLOCKED_PERMISSION`; do not claim the row was saved.

Use `tools/token-calculator.html` for interactive manual calculations when appropriate.
