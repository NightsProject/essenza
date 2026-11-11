# Compliance ranking — baseline vs fine-tuned

## Scope and method

- This ranks **pretrained baseline** and **ordinary fine-tuned generation** by compression-target compliance only. Auxiliary-guided inference is excluded.
- Primary score is the arithmetic mean of strict compliance at the 10%, 20%, and 30% targets, using the run’s reported evaluation table. Strict compliance means the generated summary is at or below its requested word-count cap. Scores are shown per target so the average cannot hide where a model succeeds or fails.
- This is a descriptive ranking of reported runs, not a controlled head-to-head: datasets, splits, prompts, and metric conventions differ across experiments. The late runs with 50 test sources are the most comparable subset. No run-to-run paired test is available.
- **Important interpretation:** strict compliance alone can reward summaries that are much too short. The `mean generated compression` column helps identify this failure mode. Compliance is not a quality score; consult [`model_ranking.md`](model_ranking.md) for the broader quality/compliance judgment and ROUGE-L results.

## Overall order by mean strict compliance

| Rank | Run / model | 10% | 20% | 30% | Mean strict compliance | Mean generated compression | Assessment |
|---:|---|---:|---:|---:|---:|---|---|
| 1 | Experiment 10 — fine-tuned, loss weight 0 | 48% | 90% | 100% | **79.3%** | 12.71% / 13.15% / 14.58% | Highest arithmetic compliance, but over-compresses badly at 20% and 30%; not a good balanced candidate. |
| 2 | Experiment 14 — fine-tuned | 94% | 78% | 58% | **76.7%** | 7.04% / 18.06% / 29.12% | Best balanced compliance profile among later reported runs; reliable at 10/20, with 30% still weakest. |
| 3 | Experiment 4 — fine-tuned | 96% | 76% | 54% | **75.3%** | 7.12% / 17.92% / 31.11% | Strong at 10/20; 30% compliance is modest and mean compression exceeds the cap. Earlier report and protocol. |
| 4 | Experiment 11.0 — fine-tuned, weight 0.1 | 96% | 72% | 56% | **74.7%** | 6.79% / 19.83% / 29.87% | Strong 10% adherence, good 20%, weaker 30%; a sound balanced result. |
| 5 (tie) | Experiment 5 — fine-tuned | 94% | 62% | 62% | **72.7%** | 7.53% / 20.50% / 29.52% | Good 10%, moderate 20/30; paired quality gains over baseline were significant. |
| 5 (tie) | Experiment 8 — fine-tuned | 94% | 64% | 60% | **72.7%** | 7.45% / 19.78% / 29.69% | Good 10/20; slightly weaker 30%. |
| 5 (tie) | Experiment 12.0.1 — fine-tuned rerun, weight 0.1 | 94% | 60% | 64% | **72.7%** | 6.99% / 19.16% / 28.29% | Best 30% strict score among the late candidates, at the expense of 20%. |
| 8 | Experiment 6 — fine-tuned, 3e-5 LR | 94% | 64% | 58% | **72.0%** | 7.56% / 20.54% / 29.52% | Mixed LR probe; mid/high-target adherence remains a limitation. |
| 9 | Experiment 12.0.2 — fine-tuned, weight 0.01 | 94% | 62% | 58% | **71.3%** | 7.03% / 19.38% / 28.87% | Strong at 10%, moderate at 20%, weaker at 30%. |
| 10 | Experiment 13.1 — fine-tuned | 92% | 60% | 50% | **67.3%** | 7.35% / 19.84% / 29.45% | Strong short-cap compliance; weaker at 30%. |
| 11 | Experiment 13 — fine-tuned | 92% | 56% | 50% | **66.0%** | 7.31% / 20.62% / 29.49% | Weaker 20/30 adherence; config attribution is ambiguous. |
| 12 | Pretrained baseline (late standardized reports) | 0% | 26% | 54% | **26.7%** | 39.42% / 39.86% / 39.15% | Poor target conditioning: output length stays near 39–40% regardless of requested cap. |
## Corrected strict ranking

| Rank | Run / model | Strict compliance 10 / 20 / 30 | Mean |
|---:|---|---:|---:|
| 1 | Experiment 10 — fine-tuned, loss weight 0 | 48 / 90 / 100% | **79.3%** |
| 2 | Experiment 14 — fine-tuned | 94 / 78 / 58% | **76.7%** |
| 3 | Experiment 4 — fine-tuned | 96 / 76 / 54% | **75.3%** |
| 4 | Experiment 11.0 — fine-tuned, weight 0.1 | 96 / 72 / 56% | **74.7%** |
| 5 (tie) | Experiment 5 — fine-tuned | 94 / 62 / 62% | **72.7%** |
| 5 (tie) | Experiment 8 — fine-tuned | 94 / 64 / 60% | **72.7%** |
| 5 (tie) | Experiment 12.0.1 — fine-tuned rerun | 94 / 60 / 64% | **72.7%** |
| 8 | Experiment 6 — fine-tuned, 3e-5 LR | 94 / 64 / 58% | **72.0%** |
| 9 | Experiment 12.0.2 — fine-tuned, weight 0.01 | 94 / 62 / 58% | **71.3%** |
| 10 | Experiment 13.1 — fine-tuned | 92 / 60 / 50% | **67.3%** |
| 11 | Experiment 13 — fine-tuned | 92 / 56 / 50% | **66.0%** |
| 12 | Pretrained baseline (late standardized reports) | 0 / 26 / 54% | **26.7%** |

## Per-target winners

- **10% cap:** experiments 4 and 11.0 tie at 96%; experiments 5, 6, 8, 12.0.1, 12.0.2, and 14 are close at 94%. Experiment 10 is much lower at 48%.
- **20% cap:** experiment 10 leads at 90%, but its average generated compression is only 13.15%; among the better length-matched candidates, experiment 14 leads at 78%, followed by experiment 4 at 76% and experiment 11.0 at 72%.
- **30% cap:** experiment 10 reports 100%, but its average output is only 14.58% compression, so it achieves compliance through severe under-compression. Among models whose mean output is near the requested cap, experiment 12.0.1 leads at 64%, followed by experiment 5 at 62%, experiment 8 at 60%, and experiment 14 / 12.0.2 at 58%.
- **Baseline:** its 30% compliance (54%) is much better than its 10% and 20% scores, but the mean output compression is still about 39% at all three targets. The apparent 30% compliance does not mean it learned to follow the requested compression levels.

## Runs without a comparable compliance score

- Experiments 1–3 do not include a standardized aggregate baseline/fine-tuned compliance table in their run folders.
- Experiment 7 has conflicting run/config/result descriptions; its exact run-level compliance is not established.
- Experiment 9 is explicitly marked `BROKEN` and has malformed output; exclude it from candidate selection.
- Experiments 11.1, 12, and 12.0 lack a clearly attributable, ordinary fine-tuned aggregate compliance report. Any auxiliary-guided-only data is out of scope.

## Recommendation

- If selecting by the **raw three-target mean only**, experiment 10 ranks first; however, this is a misleading win because it commonly produces summaries far shorter than the 20% and 30% caps.
- For a **useful compliance candidate** that stays near the requested length and also performs well on summarization quality, experiment 14 is the strongest practical choice in the reported late runs. It is notably stronger at 20% than other balanced candidates, while experiments 5/8/12.0.1 are somewhat better at 30% strict compliance.
- The persistent weakness is the 30% cap: no ordinary fine-tuned checkpoint in this set has strong strict compliance there while also matching the desired output length consistently. Re-evaluate the shortlist on identical test sources before making fine-grained winner claims.

## Source references

- [`FineTuning/fine-tune 4/README.md`](FineTuning/fine-tune%204/README.md)
- [`FineTuning/fine-tune 5/README.md`](FineTuning/fine-tune%205/README.md)
- [`FineTuning/fine-tune 6/README.md`](FineTuning/fine-tune%206/README.md)
- [`FineTuning/fine-tune 8 with summarize semantic/README.md`](FineTuning/fine-tune%208%20with%20summarize%20semantic/README.md)
- [`FineTuning/fine-tune 10 disable auxillary loss/README.md`](FineTuning/fine-tune%2010%20disable%20auxillary%20loss/README.md)
- [`FineTuning/fine-tune 11.0 0.1/README.md`](FineTuning/fine-tune%2011.0%200.1/README.md)
- [`FineTuning/fine-tune 12.0.1 0.1 rerun/README.md`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/README.md)
- [`FineTuning/fine-tune 12.0.2 0.01/README.md`](FineTuning/fine-tune%2012.0.2%200.01/README.md)
- [`FineTuning/fine-tune 13/model_performance_metrics.csv`](FineTuning/fine-tune%2013/model_performance_metrics.csv)
- [`FineTuning/fine-tune 13.1/model_performance_metrics.csv`](FineTuning/fine-tune%2013.1/model_performance_metrics.csv)
- [`FineTuning/fine-tune 14/model_performance_metrics.csv`](FineTuning/fine-tune%2014/model_performance_metrics.csv)
- [`model_ranking.md`](model_ranking.md)
