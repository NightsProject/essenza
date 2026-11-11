# Essenza fine-tuning experiment evolution (1–14)

## Scope and reading guide

- This review follows the numbered run folders under `FineTuning/`, from experiment 1 through experiment 14, including the 13.1 follow-up as a separate run.
- The comparison is **pretrained FLAN-T5-small baseline versus ordinary fine-tuned output** only. Auxiliary-guided generation results and claims are deliberately excluded.
- “Compression” below means the observed summary-to-source word ratio, expressed as a percentage. Targets are 10%, 20%, and 30%; lower strict compliance is worse, while higher ROUGE-L F1 is better.
- Results are not perfectly apples-to-apples throughout: early experiments use 40 test sources and later runs generally use 50; splits, prompts, data sizes, training recipes, and metric/report formats also vary. Treat between-run changes as experimental signals, not controlled proof, unless the run provides a direct paired bootstrap comparison.
- Where a folder has no trustworthy baseline-vs-finetuned metric table, I say so instead of inferring exact scores. Exact source artifacts are linked in each entry.

## Run-by-run evolution

### 1 — First small-data baseline fine-tune

- **Artifacts:** [`README.md`](FineTuning/fine-tune%201/README.md), [`training_log.csv`](FineTuning/fine-tune%201/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%201/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%201/dataset_checks_report.csv).
- Started from `google/flan-t5-small`, with a simple target-conditioned prompt (“summarize to at most 10/20/30%”), 5e-5 learning rate, 5 epochs, batch size 8, and the early dataset plan (200/20/40 sources in the check report; the README config still contains an inconsistent expected-source setting of 370/50/40).
- The dataset checks passed, including split separation, completeness of the three target lengths, and no token truncation. The training log ends at 5 epochs with train loss 2.295 and final eval loss 1.997.
- Predictions show the intended behavior emerging: at 10%, the fine-tuned output is a short key-fact summary versus the pretrained baseline’s longer sentence. There is no run-level aggregate metric table here, so the size of the gain cannot be quantified from this folder alone.
- **What it established:** a working end-to-end fine-tuning/evaluation setup; the prompt and split bookkeeping needed cleanup before interpreting later results.

### 2 — Expand training set, retain 5 epochs

- **Artifacts:** [`README.md`](FineTuning/fine-tune%202/README.md), [`training_log.csv`](FineTuning/fine-tune%202/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%202/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%202/dataset_checks_report.csv).
- Increased the data plan to 370/50/40 sources, retaining 5e-5, 5 epochs, batch size 8, FP32, and Tesla T4. Validation checks passed across splits and target labels; training completed with train loss 2.177 and 695 steps.
- The test prediction file contains both pretrained baseline and fine-tuned summaries, making direct qualitative inspection possible. No aggregate metric report is present in this run folder, so it is not assigned invented numeric results.
- **Change from 1:** more training data and a now-consistent split plan; five epochs remained the reference training duration.

### 3 — Ten-epoch continuation / training-duration probe

- **Artifacts:** [`README.md`](FineTuning/fine-tune%203/README.md), [`training_log.csv`](FineTuning/fine-tune%203/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%203/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%203/dataset_checks_report.csv).
- Kept 5e-5 and batch size 8 but increased the plan to 10 epochs, reusing a runtime that already contained the epoch-5 run (explicitly noted in the README). This makes the run less clean as a from-scratch controlled comparison.
- Checks pass; train loss ends at 1.948. The logs show validation loss decreasing through early epochs, then flattening around 1.90 by the last epoch. There is no aggregate baseline-versus-finetuned score file.
- **What changed:** longer optimization reduced training loss, but the reused runtime and lack of a standardized test summary limit conclusions about generalization.

### 4 — First detailed baseline comparison

- **Artifacts:** [`README.md`](FineTuning/fine-tune%204/README.md), [`training_log.csv`](FineTuning/fine-tune%204/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%204/test_predictions.csv).
- The README provides an explicit 50-source baseline comparison (despite also describing the dataset as 370/50/40 elsewhere). Under the reported table, fine-tuning raised ROUGE-L F1 from 0.175/0.202/0.209 to 0.399/0.367/0.367 at 10/20/30%, respectively.
- Reported fine-tuned within-target rates were 96%, 76%, and 54%; the baseline’s were 10%, 60%, and 66%. The fine-tuned model improved quality substantially at every target and length control strongly at 10%/20%, but did not improve strict compliance at 30%.
- Paired bootstrap on 50 sources reported ROUGE-L gains of +0.2244, +0.1646, and +0.1574, with all 95% intervals excluding zero.
- **Interpretation:** this was the first convincing documented result that fine-tuning helps quality over the pretrained model, while revealing the 30% control weakness.

### 5 — Semantic, more explicit prompt wording

- **Artifacts:** [`README.md`](FineTuning/fine-tune%205/README.md), [`training_log.csv`](FineTuning/fine-tune%205/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%205/test_predictions.csv).
- Changed the build prompt to give target-specific semantic instructions (extremely concise / concise / moderately detailed), alongside factuality, relevance, and non-repetition requirements. The training configuration is reported as 5e-5, 15 planned epochs, batch size 8, FP32; the logged training/evaluation artifacts indicate evaluation at epoch 8.
- The reported fine-tuned ROUGE-L scores were 0.399/0.355/0.374; target compliance was 94%/62%/62%. The model’s mean observed compression was 7.527%/20.495%/29.517%.
- Paired bootstrap gains over baseline were +0.2280 [0.1744, 0.2827], +0.1184 [0.0803, 0.1544], +0.1453 [0.1047, 0.1871], all excluding zero.
- **Interpretation:** explicit semantic instructions retained the strong baseline quality gains, but mid/high-target compliance remained imperfect; the 20% and 30% scores did not dominate all previous runs.

### 6 — Lower learning rate (3e-5) probe

- **Artifacts:** [`README.md`](FineTuning/fine-tune%206/README.md), [`training_log.csv`](FineTuning/fine-tune%206/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%206/test_predictions.csv).
- The README directly compares this 3e-5 run with experiment 5’s 5e-5 run. At 10/20/30%, ROUGE-L changed 0.399→0.396, 0.355→0.367, and 0.374→0.361; compliance changed 94→94%, 62→64%, and 62→58%.
- Validation loss reached 1.9799 at epoch 12. The paired comparison against the baseline still found positive ROUGE-L gains at all targets, but this does **not** establish that 3e-5 is better than 5e-5; the README explicitly notes no paired checkpoint-to-checkpoint significance test.
- **Interpretation:** lowering the learning rate produced a mixed tradeoff, not a general improvement. The project’s own notes recommend returning attention to length conditioning rather than continuing LR tweaks.

### 7 — Official control / explicit word-count prompt

- **Artifacts:** [`READEME.md`](FineTuning/fine-tune%207%20official%20baseline/READEME.md), [`training_log.csv`](FineTuning/fine-tune%207%20official%20baseline/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%207%20official%20baseline/test_predictions.csv).
- Labeled “official baseline” in the folder, but this is a **fine-tuned control checkpoint**, not the pretrained baseline: the README itself distinguishes those concepts. It uses FLAN-T5-small, 3e-5, 15 epochs, and a prompt containing source word count and computed maximum summary word count.
- The README also records a recommended 5e-5 control table (ROUGE-L 0.412/0.360/0.367; compliance 96/68/50%) and bootstrap gains +0.2211/+0.1025/+0.1231. These are presented as established control results, but differ from the stated 3e-5 config and therefore should not be silently treated as this folder’s exact run output.
- Dataset validation passed. Training log shows evaluation to epoch 9, not the stated 15. No run-specific aggregate metric CSV is included.
- **Interpretation:** this run documents a more explicit prompt and the correct distinction between pretrained baseline and fine-tuned control; inconsistent README/config/result provenance makes exact run attribution uncertain.

### 8 — Semantic compression-conditioning experiment

- **Artifacts:** [`README.md`](FineTuning/fine-tune%208%20with%20summarize%20semantic/README.md), [`training_log.csv`](FineTuning/fine-tune%208%20with%20summarize%20semantic/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%208%20with%20summarize%20semantic/test_predictions.csv).
- Used semantic compression prompts, 5e-5, batch size 8, FP32; the folder reports an 8-epoch final evaluation despite a 15-epoch planned run. Validation loss bottomed at 1.9798 (epoch 5).
- Fine-tuned ROUGE-L was 0.398/0.370/0.352; within-target rates 94/64/60%; observed compression 7.449/19.781/29.685%.
- Bootstrap improvements over baseline: +0.1846 [0.1391, 0.2323], +0.1156 [0.0767, 0.1544], +0.0989 [0.0645, 0.1348] (all intervals exclude zero).
- **Interpretation:** semantic conditioning improved the pretrained baseline at every cap, but the 30% quality score was lower than experiment 5’s reported score; no paired test between the two fine-tuned runs is supplied.

### 9 — Custom-loss attempt (marked broken)

- **Artifacts:** [`dataset_checks_report.csv`](FineTuning/fine-tune%209%20with%20costum%20loss%20-%20BROKEN/dataset_checks_report.csv), [`training_log.csv`](FineTuning/fine-tune%209%20with%20costum%20loss%20-%20BROKEN/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%209%20with%20costum%20loss%20-%20BROKEN/test_predictions.csv).
- The directory is explicitly named **BROKEN**. Dataset checks mostly pass, but do not validate the correctness of the custom objective or its outputs.
- Training log shows a concerning eval loss of 6.721 at epoch 19; test predictions include an obvious malformed, repetitive token-like summary (“The The's a million-meter…”), unlike the readable baseline and earlier fine-tuned outputs.
- No trustworthy aggregate comparison is provided. This run should be excluded from candidate ranking and not presented as a successful model.
- **Interpretation:** a failed custom-loss implementation; its value is diagnostic, not competitive.

### 10 — Auxiliary loss disabled (weight 0)

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2010%20disable%20auxillary%20loss/README.md), [`training_log (1).csv`](FineTuning/fine-tune%2010%20disable%20auxillary%20loss/training_log%20%281%29.csv), [`test_predictions.csv`](FineTuning/fine-tune%2010%20disable%20auxillary%20loss/test_predictions.csv).
- Set `LENGTH_LOSS_WEIGHT=0.0` to test the effect of removing the length objective; used 1e-5, 5 epochs, batch size 8, FP32 on the expanded 540/110/50 data.
- Reported fine-tuned ROUGE-L was 0.355/0.281/0.262 (baseline 0.226/0.266/0.262); compliance was 48/90/100%, with means 12.711/13.153/14.579% compression. Bootstrap baseline gains were significant at 10% (+0.1286, CI [0.0944, 0.1621]) but not at 20% (+0.0150, CI crossing zero) or 30% (-0.0002, CI crossing zero).
- **Interpretation:** removing the length loss gave very strong reported compliance at 20/30 only by producing outputs substantially shorter than the requested targets; quality gains over baseline were weak or absent at 20/30. It was not a balanced overall result.

### 11 — Length-aware model, loss weight 0.1

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2011.0%200.1/README.md), [`training_log.csv`](FineTuning/fine-tune%2011.0%200.1/training_log.csv), [`test_predictions%20%281%29.csv`](FineTuning/fine-tune%2011.0%200.1/test_predictions%20%281%29.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2011.0%200.1/dataset_checks_report.csv).
- Introduced the length-aware model with auxiliary loss weight 0.1, 5e-5, and an expanded 540/110/50 split. Although 50 epochs were configured, the README and logs report the run ending at epoch 8; validation loss was 1.9848.
- The README gives baseline-versus-finetuned results: ROUGE-L 0.404/0.360/0.373 versus 0.226/0.266/0.262; observed compression 6.789/19.826/29.867%; compliance 96/72/56%.
- Paired bootstrap ROUGE-L gains were +0.1782 [0.1299, 0.2254], +0.0935 [0.0628, 0.1247], +0.1111 [0.0803, 0.1424], all excluding zero. Dataset checks passed, with a minor tokenizer round-trip warning (3/4200 texts).
- **Interpretation:** first strong auxiliary-loss checkpoint in the ordinary fine-tuned comparison: substantial quality improvements and improved length control, especially at 10%; 30% remained the weakest compliance point.

### 11.1 — Loss-weight 0.2 variant

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2011.1%20auxilary%200.2/README.md), [`training_log.csv`](FineTuning/fine-tune%2011.1%20auxilary%200.2/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%2011.1%20auxilary%200.2/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2011.1%20auxilary%200.2/dataset_checks_report.csv).
- Tested weight 0.2; the README is empty. Training log shows 8 epochs and eval loss 1.9849; dataset checks pass except the same 3/4200 tokenizer round-trip warning.
- There is no model performance table or paired-bootstrap report. The predictions permit qualitative inspection but do not justify numeric ranking against 11.0 or later runs.
- **Interpretation:** documented training variant, but incomplete evaluation record; retain as an unranked exploratory checkpoint.

### 12 — Weight 0.5, first higher-weight run

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2012%20.5/README.md), [`training_log.csv`](FineTuning/fine-tune%2012%20.5/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%2012%20.5/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2012%20.5/dataset_checks_report.csv).
- Used 0.5 auxiliary weight, 5e-5, with 50 epochs configured; README records 8 completed epochs and validation loss 1.9816. Dataset checks pass with a 3/4200 tokenizer warning.
- This folder lacks a trustworthy summary metrics CSV; do not confuse the test prediction file’s sample rows with aggregate scores. It is a precursor to the later 12.0.x follow-ups, not enough to rank quantitatively on its own.
- **Interpretation:** higher weight tested; evidence in the folder is insufficient to claim it improved baseline-relative quality or compression behavior.

### 12.0 — Rebuilt prompt, loss weight 0.2

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2012.0%20new%20build%20prompt/README.md), [`training_log.csv`](FineTuning/fine-tune%2012.0%20new%20build%20prompt/training_log.csv), [`test_predictions.csv`](FineTuning/fine-tune%2012.0%20new%20build%20prompt/test_predictions.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2012.0%20new%20build%20prompt/dataset_checks_report.csv).
- Rebuilt prompt variant with reported auxiliary weight 0.2, 5e-5 and 50 epochs configured; training log documents 8 epochs, eval loss 1.9818. Data checks pass, with the 3/4200 tokenizer warning.
- No baseline-vs-finetuned metric table is included, so it is not numerically rankable from this folder.
- **Interpretation:** prompt/build iteration whose experiment value cannot be isolated quantitatively without the missing evaluation output.

### 12.0.1 — Weight 0.1 rerun

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/README.md), [`training_log.csv`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/training_log.csv), [`test_predictions_aux_guided.csv`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/test_predictions_aux_guided.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2012.0.1%200.1%20rerun/dataset_checks_report.csv).
- The README reports baseline-vs-finetuned scores: ROUGE-L 0.378/0.370/0.388 versus 0.208/0.251/0.252; compliance 94/60/64%; mean compression 6.992/19.160/28.288%.
- Paired bootstrap gains are +0.1700 [0.1120, 0.2276], +0.1184 [0.0827, 0.1520], +0.1367 [0.1022, 0.1707], all significant. Evaluation includes 50 sources and the data checks pass with the tokenizer warning.
- **Interpretation:** solid balanced result: statistically supported quality gains at all caps, with better-than-baseline compliance at 10/20/30. However, the named prediction artifact is auxiliary-guided; per scope, those outputs are excluded from this comparison.

### 12.0.2 — Weight 0.01 rerun

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2012.0.2%200.01/README.md), [`training_log.csv`](FineTuning/fine-tune%2012.0.2%200.01/training_log.csv), [`test_predictions_aux_guided.csv`](FineTuning/fine-tune%2012.0.2%200.01/test_predictions_aux_guided.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2012.0.2%200.01/dataset_checks_report.csv).
- Tried a much smaller 0.01 weight after project notes described stronger weights as too aggressive for compression. Training log reports 8 epochs and eval loss 1.9797; dataset checks pass with the tokenizer warning.
- README metrics: fine-tuned ROUGE-L 0.386/0.369/0.386; mean compression 7.030/19.381/28.869%; compliance 94/62/58%. Paired baseline gains +0.1778 [0.1192,0.2353], +0.1174 [0.0834,0.1498], +0.1340 [0.1002,0.1679] are significant at all targets.
- **Interpretation:** quality is robust across all caps and baseline gains are clear; 30% compliance remains weaker than 10/20. Auxiliary-guided predictions are intentionally ignored here.

### 13 — Length head revised; loss-weight/model-target handoff

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2013/README.md), [`model_performance_metrics.csv`](FineTuning/fine-tune%2013/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2013/paired_bootstrap_results.csv), [`training_log.csv`](FineTuning/fine-tune%2013/training_log.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2013/dataset_checks_report.csv).
- The README describes a revised length head: pass the requested cap as `target_caps`, condition a pooled encoder representation on the cap embedding, predict cap utilisation, and use MSE; it describes raising the length-loss weight from 0.01 to 0.1. The README header/config separately says auxiliary loss weight 0.5, so exact configured-versus-described weight is ambiguous.
- Ordinary fine-tuned results: ROUGE-L 0.368/0.360/0.379; mean compression 7.307/20.623/29.487%; strict compliance 92/56/50% (tolerant 96/66/58%). Baseline is 0.208/0.251/0.252 ROUGE-L, with 0/26/54% strict compliance.
- Paired bootstrap confirms significant ROUGE-L improvements over baseline at each target: +0.1605 [0.1036,0.2172], +0.1088 [0.0742,0.1413], +0.1278 [0.0914,0.1642]. Compliance improves at 10 and 20; the 30% strict-compliance difference is not significant.
- **Interpretation:** quality remains decisively better than pretrained baseline, but this checkpoint’s 20/30 compliance trails later 14; the inconsistent loss-weight description should be resolved before attributing effects.

### 13.1 — Follow-up with revised reporting/selection details

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2013.1/README.md), [`model_performance_metrics.csv`](FineTuning/fine-tune%2013.1/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2013.1/paired_bootstrap_results.csv), [`training_log.csv`](FineTuning/fine-tune%2013.1/training_log.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2013.1/dataset_checks_report.csv).
- Uses the 540/110/50 data plan and records 0.5 auxiliary loss weight, 5e-5 learning rate, and 8 completed epochs. README documents length-head and generation-selection changes, but those guided-inference results are out of scope.
- Ordinary fine-tuned scores: ROUGE-L 0.372/0.362/0.370; mean compression 7.349/19.837/29.448%; strict compliance 92/60/50% (tolerant 96/68/60%). Baseline ROUGE-L is 0.208/0.251/0.252; strict compliance 0/26/54%.
- Paired bootstrap quality gains are +0.1641 [0.1073,0.2210], +0.1105 [0.0772,0.1420], +0.1181 [0.0828,0.1531], all significant. 30% strict compliance is still not significantly better than baseline.
- **Interpretation:** broadly similar to 13; slight movement at 20%, no consistent quality/compliance dominance. It improves the written methodology and dataset coverage, not the evidence of universal run-to-run superiority.

### 14 — Higher learning rate, strongest overall ordinary fine-tuned result

- **Artifacts:** [`README.md`](FineTuning/fine-tune%2014/README.md), [`model_performance_metrics.csv`](FineTuning/fine-tune%2014/model_performance_metrics.csv), [`paired_bootstrap_results.csv`](FineTuning/fine-tune%2014/paired_bootstrap_results.csv), [`training_log.csv`](FineTuning/fine-tune%2014/training_log.csv), [`dataset_checks_report.csv`](FineTuning/fine-tune%2014/dataset_checks_report.csv).
- Compared with 13/13.1, the reported learning rate is doubled from 5e-5 to 1e-4; same expanded 540/110/50 data and batch size 8. Though 10 epochs are listed, training stopped at epoch 7; the best logged validation loss was 1.9690 at epoch 4. Dataset checks pass, with a warning that 3/4200 strings change after tokenizer round trip.
- Ordinary fine-tuned results: ROUGE-L 0.391/0.358/0.390; actual compression 7.037/18.062/29.121%; strict compliance 94/78/58% (tolerant 98/84/68%). Baseline is ROUGE-L 0.208/0.251/0.252 and compliance 0/26/54%.
- Paired bootstrap baseline-relative ROUGE-L gains: +0.1826 [0.1262,0.2371], +0.1064 [0.0739,0.1382], +0.1383 [0.1041,0.1714]; all intervals exclude zero. Strict-compliance improvements are significant at 10 and 20; 30% is not.
- **Interpretation:** best-balanced available ordinary fine-tuned run in the numbered set: strongest or near-strongest quality at 10/30, best 20% strict compliance among documented runs, and meaningful gains over pretrained baseline at every cap. It is not a statistically proven winner over other fine-tuned checkpoints because cross-run paired tests are absent.

## Overall trajectory

- The progression moved from a basic prompt and small dataset (1–3), to evidence that fine-tuning beats the pretrained model on ROUGE-L (4–8), then into explicit length-aware objectives and loss-weight tuning (9–13.1), and finally a higher-LR run (14).
- The pretrained baseline is consistently poor at obeying short compression targets: by the standardized later test set it averages about 39–40% compression for all three target values, with strict compliance of 0%, 26%, and 54%.
- Fine-tuning consistently raises ROUGE-L over baseline at 10%, 20%, and 30% in runs that include paired-bootstrap evidence. In the latest consistent set, gains are roughly +0.11 to +0.18 ROUGE-L, all statistically supported within each run.
- Compression control is strongest at 10%, generally good at 20% in later experiments, and the persistent weak spot is strict compliance at 30%; most fine-tuned runs do not show a statistically significant 30% strict-compliance lift over baseline.
- Do not read lower compression percentages as automatically better: the human references average 7.86%, 16.86%, and 26.05% for the nominal 10/20/30 targets. Matching the target cap and matching human reference length are distinct goals.
- Experiment 9 is a clear failed implementation. Experiments 11.1, 12, and 12.0 are incompletely reported and should remain unranked pending standardized metrics.
- **Current practical takeaway:** experiment 14 is the best-supported overall ordinary fine-tuned candidate, while experiment 11.0 is the clearest earlier quality/compression-balanced result. Keep the pretrained baseline as the reference comparator, not as the deployment candidate.
