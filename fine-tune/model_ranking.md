# Essenza model ranking — baseline vs fine-tuned only

## Scope and ranking method

- This ranks the **pretrained baseline** and the ordinary **fine-tuned** outputs from experiments 1–14. Auxiliary-guided inference results are excluded, including any apparent gain from post-generation candidate selection or budget enforcement.
- Primary evidence: later standardized 50-source baseline comparisons with ROUGE-L F1, strict cap compliance, and paired bootstrap confidence intervals. ROUGE-L is treated as quality; strict compliance as cap adherence. Both matter, so the rank is an evidence-weighted practical judgment, not a single metric sort.
- Runs with no aggregate metrics are marked unranked, not assigned guessed scores. Cross-run tests generally compare each fine-tuned run to its own baseline; they do not establish statistical significance between fine-tuned checkpoints.

## Overall ranking (ordinary fine-tuned candidates)

### 1. Experiment 14 — best balanced candidate

- **ROUGE-L F1 (10/20/30):** 0.391 / 0.358 / 0.390.
- **Actual compression:** 7.04% / 18.06% / 29.12%.
- **Strict compliance:** 94% / 78% / 58%; tolerant: 98% / 84% / 68%.
- **Paired baseline gains:** +0.1826 [0.1262, 0.2371], +0.1064 [0.0739, 0.1382], +0.1383 [0.1041, 0.1714]; each CI excludes zero.
- **Why #1:** strongest balanced evidence across all targets: high 10/30 quality, best documented strict 20% compliance, strong compression match, and significant quality gain over the paired baseline at every cap. 30% compliance remains only 58%, and the run stopped at epoch 7 despite the 10-epoch plan.
- **Source:** [`FineTuning/fine-tune 14/model_performance_metrics.csv`](FineTuning/fine-tune%2014/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2014/paired_bootstrap_results.csv), [`README.md`](FineTuning/fine-tune%2014/README.md).

### 2. Experiment 11.0 (weight 0.1) — strongest early balanced model

- **ROUGE-L F1:** 0.404 / 0.360 / 0.373.
- **Actual compression:** 6.789% / 19.826% / 29.867%.
- **Strict compliance:** 96% / 72% / 56%.
- **Paired baseline gains:** +0.1782 [0.1299, 0.2254], +0.0935 [0.0628, 0.1247], +0.1111 [0.0803, 0.1424]; all significant.
- **Why #2:** very strong 10% quality and compliance, with significant baseline-relative quality gains across all caps. It loses to 14 on 20% strict compliance and documented 30% quality/compression balance; exact fine-tuned-to-fine-tuned significance is unknown.
- **Source:** [`FineTuning/fine-tune 11.0 0.1/README.md`](FineTuning/fine-tune%2011.0%200.1/README.md), [`training_log.csv`](FineTuning/fine-tune%2011.0%200.1/training_log.csv).

### 3. Experiment 12.0.2 (weight 0.01) — strong quality, weaker 30% adherence

- **ROUGE-L F1:** 0.386 / 0.369 / 0.386.
- **Actual compression:** 7.030% / 19.381% / 28.869%.
- **Strict compliance:** 94% / 62% / 58%.
- **Paired baseline gains:** +0.1778 [0.1192, 0.2353], +0.1174 [0.0834, 0.1498], +0.1340 [0.1002, 0.1679]; all significant.
- **Why #3:** consistently high quality and close-to-target means; its 20% compliance trails 14 and 11.0, with no fine-tuned-versus-fine-tuned test to resolve small ROUGE differences.
- **Source:** [`FineTuning/fine-tune 12.0.2 0.01/README.md`](FineTuning/fine-tune%2012.0.2%200.01/README.md), [`training_log.csv`](FineTuning/fine-tune%2012.0.2%200.01/training_log.csv).

### 4. Experiment 12.0.1 (weight 0.1 rerun) — reliable quality gains, variable adherence

- **ROUGE-L F1:** 0.378 / 0.370 / 0.388.
- **Actual compression:** 6.992% / 19.160% / 28.288%.
- **Strict compliance:** 94% / 60% / 64%.
- **Paired baseline gains:** +0.1700 [0.1120, 0.2276], +0.1184 [0.0827, 0.1520], +0.1367 [0.1022, 0.1707]; all significant.
- **Why #4:** good 30% ROUGE and significant gains, but reported strict adherence at 20% is lower than the stronger candidates. Any aux-guided-only rows in this folder were deliberately excluded.
- **Source:** [`FineTuning/fine-tune 12.0.1 0.1 rerun/README.md`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/README.md), [`training_log.csv`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/training_log.csv).

### 5. Experiment 13.1 — sound gains, weakest documented 30% strict score

- **ROUGE-L F1:** 0.372 / 0.362 / 0.370.
- **Actual compression:** 7.349% / 19.837% / 29.448%.
- **Strict compliance:** 92% / 60% / 50%.
- **Paired baseline gains:** +0.1641 [0.1073, 0.2210], +0.1105 [0.0772, 0.1420], +0.1181 [0.0828, 0.1531]; all significant.
- **Why #5:** statistically clear quality improvement over baseline, but does not lead on the main quality or strict-compliance dimensions among the fully reported later candidates.
- **Source:** [`FineTuning/fine-tune 13.1/model_performance_metrics.csv`](FineTuning/fine-tune%2013.1/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2013.1/paired_bootstrap_results.csv).

### 6. Experiment 13 — quality gains but lower 20/30 compliance

- **ROUGE-L F1:** 0.368 / 0.360 / 0.379.
- **Actual compression:** 7.307% / 20.623% / 29.487%.
- **Strict compliance:** 92% / 56% / 50%.
- **Paired baseline gains:** +0.1605 [0.1036, 0.2172], +0.1088 [0.0742, 0.1413], +0.1278 [0.0914, 0.1642]; all significant.
- **Why #6:** the 30% ROUGE is competitive, but the 20% and 30% strict adherence results are weaker than the other well-documented late-stage choices. README and config disagree on loss weight, which weakens interpretability.
- **Source:** [`FineTuning/fine-tune 13/model_performance_metrics.csv`](FineTuning/fine-tune%2013/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2013/paired_bootstrap_results.csv), [`README.md`](FineTuning/fine-tune%2013/README.md).

### 7. Experiment 5 — good quality; moderate 20/30 compliance

- **ROUGE-L F1:** 0.399 / 0.355 / 0.374.
- **Actual compression:** 7.527% / 20.495% / 29.517%.
- **Within-target rates:** 94% / 62% / 62%.
- **Paired baseline gains:** +0.2280 [0.1744, 0.2827], +0.1184 [0.0803, 0.1544], +0.1453 [0.1047, 0.1871]; all significant.
- **Why #7:** excellent quality at 10% and strong baseline-relative gains; later models provide a more complete strict/tolerant compliance report and generally better 20% adherence.
- **Source:** [`FineTuning/fine-tune 5/README.md`](FineTuning/fine-tune%205/README.md).

### 8. Experiment 8 — consistent gains; weaker 30% quality

- **ROUGE-L F1:** 0.398 / 0.370 / 0.352.
- **Actual compression:** 7.449% / 19.781% / 29.685%.
- **Within-target rates:** 94% / 64% / 60%.
- **Paired baseline gains:** +0.1846 [0.1391, 0.2323], +0.1156 [0.0767, 0.1544], +0.0989 [0.0645, 0.1348]; all significant.
- **Why #8:** strong at 10/20, but its 30% ROUGE is lower than later alternatives; no cross-run paired checkpoint test.
- **Source:** [`FineTuning/fine-tune 8 with summarize semantic/README.md`](FineTuning/fine-tune%208%20with%20summarize%20semantic/README.md).

### 9. Experiment 4 — strong early result, mixed cap adherence

- **ROUGE-L F1:** 0.399 / 0.367 / 0.367.
- **Actual compression:** 7.120% / 17.920% / 31.109%.
- **Within-target rates:** 96% / 76% / 54%.
- **Paired baseline gains:** +0.2244 / +0.1646 / +0.1574; all reported 95% CIs exclude zero.
- **Why #9:** historically important and strong by ROUGE, particularly at 20%, but it exceeds the 30% cap on average and uses earlier/less consistent data reporting than late runs.
- **Source:** [`FineTuning/fine-tune 4/README.md`](FineTuning/fine-tune%204/README.md).

### 10. Experiment 10 — loss disabled; over-compresses 20/30

- **ROUGE-L F1:** 0.355 / 0.281 / 0.262 (baseline: 0.226 / 0.266 / 0.262).
- **Actual compression:** 12.711% / 13.153% / 14.579%.
- **Within-target rates:** 48% / 90% / 100%.
- **Paired baseline ROUGE gains:** significant only at 10%; 20% and 30% CIs include zero.
- **Why #10:** high compliance at the looser settings is misleading because outputs are much shorter than the requested levels; quality is not improved at 20/30.
- **Source:** [`FineTuning/fine-tune 10 disable auxillary loss/README.md`](FineTuning/fine-tune%2010%20disable%20auxillary%20loss/README.md).

### 11. Experiments 1–3 — foundational, not quantitatively rankable

- Have README/config, training logs, prediction CSVs and dataset check reports, but no reliable standardized aggregate baseline-versus-finetuned evaluation table in their own folders.
- Experiment 1 is especially early and contains a mismatch between the checked split sizes and README expected-source config; experiment 3 notes a reused runtime.
- **Status:** useful development milestones; insufficient comparable evidence for placement by score.
- **Sources:** [`FineTuning/fine-tune 1/`](FineTuning/fine-tune%201/), [`FineTuning/fine-tune 2/`](FineTuning/fine-tune%202/), [`FineTuning/fine-tune 3/`](FineTuning/fine-tune%203/).

### 12. Experiments 7 and 11.1 — incomplete or provenance-ambiguous results

- Experiment 7’s README calls itself an “official baseline” but documents a fine-tuned control, has a 3e-5 config alongside 5e-5 control results, and a training log ending at epoch 9; exact run-specific metrics are not established.
- Experiment 11.1 has an empty README, training/evaluation logs and prediction CSVs, but no aggregate model metric table or paired bootstrap.
- **Status:** do not numerically rank until the run identity and same-protocol baseline comparison are made explicit.
- **Sources:** [`FineTuning/fine-tune 7 official baseline/READEME.md`](FineTuning/fine-tune%207%20official%20baseline/READEME.md), [`FineTuning/fine-tune 11.1 auxilary 0.2/README.md`](FineTuning/fine-tune%2011.1%20auxilary%200.2/README.md).

### Excluded: Experiment 9 — broken custom loss

- The folder is explicitly labeled `BROKEN`, training/evaluation logs show an eval loss of 6.721 at epoch 19, and sample output is malformed/repetitive. It is not a viable candidate.
- **Source:** [`FineTuning/fine-tune 9 with costum loss - BROKEN/test_predictions.csv`](FineTuning/fine-tune%209%20with%20costum%20loss%20-%20BROKEN/test_predictions.csv), [`training_log.csv`](FineTuning/fine-tune%209%20with%20costum%20loss%20-%20BROKEN/training_log.csv).

## Pretrained baseline reference

The standardized late-run baseline is effectively the same across experiments 13/13.1/14:

| Target | ROUGE-L F1 | Mean compression | Strict compliance |
|---:|---:|---:|---:|
| 10% | 0.208 | 39.42% | 0% |
| 20% | 0.251 | 39.86% | 26% |
| 30% | 0.252 | 39.15% | 54% |

- The baseline’s main failure is target conditioning: it generates roughly 39–40% compression at every requested target.
- On later matched 50-source tests, every fully reported candidate above improves ROUGE-L significantly over its own baseline at all three targets.
- Fine-tuned models generally fix the short-cap behavior, but no documented run makes 30% strict compliance a settled strength.
- Human reference compression averages 7.86%, 16.86%, and 26.05%; the model’s target compliance and closeness to reference lengths should both remain in the evaluation dashboard.

## Bottom line

- **Candidate to carry forward:** experiment 14, as the best practical balance across quality and length adherence in the available ordinary fine-tuned results.
- **Strong alternatives:** 11.0 for 10% quality/compliance; 12.0.2 for strong ROUGE across targets; 12.0.1 for its relatively strong 30% compliance/quality profile.
- **Evidence caveat:** this is an informed ranking from reported aggregates, not a statistically tested ordering among checkpoints. To make that claim, re-evaluate the shortlisted models on identical source IDs and run paired bootstrap comparisons between the fine-tuned outputs.
