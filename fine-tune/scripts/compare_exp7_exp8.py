#!/usr/bin/env python3
"""Compare experiment 7 and 8 fine-tuned predictions on paired test examples.

Defaults use each experiment's test_predictions.csv. Rows are aligned by
(source_id, target_length), and source/reference text is checked for agreement.
Writes paired per-example metrics, aggregate metrics and bootstrap intervals.
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'FineTuning'
DEFAULT_EXP7 = ROOT / 'fine-tune 7 official baseline' / 'test_predictions.csv'
DEFAULT_EXP8 = ROOT / 'fine-tune 8 with summarize semantic' / 'test_predictions.csv'
WORD_RE = re.compile(r"\b[\w]+(?:['’][\w]+)?\b", re.UNICODE)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text.casefold())


def rouge_l_f1(reference: str, candidate: str) -> float:
    """Compute ROUGE-L F1 using token-level longest common subsequence."""
    ref, hyp = words(reference), words(candidate)
    if not ref or not hyp:
        return 1.0 if not ref and not hyp else 0.0
    # One-row dynamic program: O(len(reference) * len(candidate)) time,
    # O(min(len(reference), len(candidate))) memory.
    if len(hyp) > len(ref):
        ref, hyp = hyp, ref
    previous = [0] * (len(hyp) + 1)
    for token in ref:
        current = [0]
        for j, other in enumerate(hyp, 1):
            current.append(previous[j - 1] + 1 if token == other else max(previous[j], current[-1]))
        previous = current
    lcs = previous[-1]
    precision, recall = lcs / len(hyp), lcs / len(ref)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def read_predictions(path: Path, summary_column: str) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        required = {'source_id', 'source', 'target_length', 'reference_summary', summary_column}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path}: missing required columns: {sorted(missing)}')
        results = {}
        for line_num, row in enumerate(reader, 2):
            key = (row['source_id'].strip(), row['target_length'].strip())
            if not key[0] or not key[1]:
                raise ValueError(f'{path}:{line_num}: source_id/target_length is empty')
            if key in results:
                raise ValueError(f'{path}:{line_num}: duplicate key {key}')
            results[key] = {
                'source_id': key[0], 'target_length': key[1],
                'source': row['source'], 'reference_summary': row['reference_summary'],
                'summary': row[summary_column],
            }
    if not results:
        raise ValueError(f'{path}: no prediction rows')
    return results


def paired_rows(exp7: dict, exp8: dict) -> list[dict[str, str]]:
    keys7, keys8 = set(exp7), set(exp8)
    if keys7 != keys8:
        raise ValueError(
            f'Prediction keys differ: exp7 has {len(keys7)}, exp8 has {len(keys8)}, '
            f'shared={len(keys7 & keys8)}; exp7-only={sorted(keys7-keys8)[:5]}, '
            f'exp8-only={sorted(keys8-keys7)[:5]}'
        )
    paired = []
    for key in sorted(keys7, key=lambda k: (k[0], int(k[1]))):
        a, b = exp7[key], exp8[key]
        if a['source'] != b['source']:
            raise ValueError(f'Source text differs for paired example {key}')
        if a['reference_summary'] != b['reference_summary']:
            raise ValueError(f'Reference summary differs for paired example {key}')
        source_words = len(words(a['source']))
        if source_words == 0:
            raise ValueError(f'Empty source for paired example {key}')
        cap = float(key[1])
        if cap <= 0:
            raise ValueError(f'Invalid target_length {key[1]} for {key}')
        ref = a['reference_summary']
        for label, record in (('exp7', a), ('exp8', b)):
            summary = record['summary']
            n_summary = len(words(summary))
            paired.append({
                'source_id': key[0], 'target_length': key[1], 'experiment': label,
                'source_word_count': str(source_words), 'summary_word_count': str(n_summary),
                'actual_compression_percent': f'{100*n_summary/source_words:.6f}',
                'within_target': str(100*n_summary/source_words <= cap + 1e-12),
                'rougeL_f1': f'{rouge_l_f1(ref, summary):.8f}',
                'summary': summary,
            })
    return paired


def summarize_predictions(rows: list[dict[str, str]]) -> dict[str, float]:
    n = len(rows)
    actual_ratios = [float(r['actual_compression_percent']) if 'actual_compression_percent' in r
                     else 100 * len(words(r['summary'])) / len(words(r['source'])) for r in rows]
    compliance = [r['within_target'] == 'True' if 'within_target' in r
                  else 100 * len(words(r['summary'])) / len(words(r['source'])) <= float(r['target_length'])
                  for r in rows]
    rouge = [float(r['rougeL_f1']) if 'rougeL_f1' in r
             else rouge_l_f1(r['reference_summary'], r['summary']) for r in rows]
    return {
        'n_examples': n,
        'actual_compression_percent': sum(actual_ratios) / n,
        'within_target_percent': 100 * sum(compliance) / n,
        'rougeL_f1': sum(rouge) / n,
    }
 


def bootstrap_difference(rows7: list[dict[str, str]], rows8: list[dict[str, str]],
                         metric: str, iterations: int, seed: int) -> tuple[float, float, float]:
    """Paired percentile bootstrap CI, resampling source IDs as clusters."""
    by_source7: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_source8: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows7: by_source7[r['source_id']].append(r)
    for r in rows8: by_source8[r['source_id']].append(r)
    ids = sorted(by_source7)
    if ids != sorted(by_source8):
        raise ValueError('Bootstrap inputs do not have matching source IDs')

    def value(records: list[dict[str, str]]) -> float:
        if metric == 'within_target_percent':
            return 100 * sum(r['within_target'] == 'True' for r in records) / len(records)
        return sum(float(r[metric]) for r in records) / len(records)

    point = value(rows8) - value(rows7)
    rng = random.Random(seed)
    diffs = []
    for _ in range(iterations):
        sampled = [rng.choice(ids) for _ in ids]
        sample7 = [r for sid in sampled for r in by_source7[sid]]
        sample8 = [r for sid in sampled for r in by_source8[sid]]
        diffs.append(value(sample8) - value(sample7))
    diffs.sort()
    lo = diffs[int(0.025 * (iterations - 1))]
    hi = diffs[int(0.975 * (iterations - 1))]
    return point, lo, hi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exp7', type=Path, default=DEFAULT_EXP7)
    parser.add_argument('--exp8', type=Path, default=DEFAULT_EXP8)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'comparison_exp7_vs_exp8')
    parser.add_argument('--bootstrap-iterations', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.bootstrap_iterations < 100:
        parser.error('--bootstrap-iterations must be at least 100')

    exp7 = read_predictions(args.exp7, 'finetuned_summary')
    exp8 = read_predictions(args.exp8, 'finetuned_summary')
    paired = paired_rows(exp7, exp8)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    detail_path = args.output_dir / 'paired_predictions.csv'
    with detail_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader(); writer.writerows(paired)

    aggregate = []
    comparison = []
    for cap in sorted({r['target_length'] for r in paired}, key=int):
        subset = [r for r in paired if r['target_length'] == cap]
        by_exp = {e: [r for r in subset if r['experiment'] == e] for e in ('exp7', 'exp8')}
        metrics = {e: summarize_predictions(by_exp[e]) for e in by_exp}
        for exp, m in metrics.items():
            aggregate.append({'target_length': cap, 'experiment': exp, **m})
        for metric in ('rougeL_f1', 'actual_compression_percent', 'within_target_percent'):
            point, lo, hi = bootstrap_difference(by_exp['exp7'], by_exp['exp8'], metric,
                                                   args.bootstrap_iterations, args.seed + int(cap))
            comparison.append({
                'target_length': cap, 'metric': metric, 'difference_exp8_minus_exp7': point,
                'ci95_low': lo, 'ci95_high': hi,
                'ci_excludes_zero': lo > 0 or hi < 0,
                'bootstrap_iterations': args.bootstrap_iterations,
                'bootstrap_unit': 'source_id (paired cluster bootstrap)',
            })

    for filename, records in (('aggregate_metrics.csv', aggregate), ('paired_bootstrap.csv', comparison)):
        with (args.output_dir / filename).open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)

    print(f'Paired examples: {len(paired)} ({len(exp7)} unique (source_id, target_length) keys)')
    print(f'Output directory: {args.output_dir}')
    print('\nAggregate metrics by target cap:')
    for r in aggregate:
        print(f"  {r['target_length']}% {r['experiment']}: ROUGE-L={r['rougeL_f1']:.4f}; "
              f"actual compression={r['actual_compression_percent']:.2f}%; "
              f"within cap={r['within_target_percent']:.1f}%")
    print('\nPaired bootstrap (experiment 8 minus experiment 7; 95% percentile CI):')
    for r in comparison:
        print(f"  {r['target_length']}% {r['metric']}: {r['difference_exp8_minus_exp7']:.4f} "
              f"[{r['ci95_low']:.4f}, {r['ci95_high']:.4f}]")
    print('\nNote: ROUGE-L is token-level overlap, not factuality. Bootstrap intervals quantify sampling uncertainty on these test sources; they do not control for training-run randomness.')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, csv.Error) as exc:
        print(f'error: {exc}', file=sys.stderr)
        raise SystemExit(2)
