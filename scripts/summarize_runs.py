#!/usr/bin/env python3
"""Summarise the run log: success rate, times and failure causes.

    python3 scripts/summarize_runs.py                 # all rows of ~/hcw_ws/results/runs.csv
    python3 scripts/summarize_runs.py --from-run 7    # only rows with run_id >= 7
    python3 scripts/summarize_runs.py --csv other.csv
"""
import argparse
import collections
import csv
import os
import statistics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=os.path.expanduser('~/hcw_ws/results/runs.csv'))
    ap.add_argument('--from-run', type=int, default=1)
    args = ap.parse_args()
    with open(args.csv, newline='') as f:
        rows = [r for r in csv.DictReader(f) if int(r['run_id']) >= args.from_run]
    if not rows:
        print('no runs found')
        return 1

    def rate(sub):
        ok = sum(r['success'] == 'yes' for r in sub)
        return '%d / %d = %.0f %%' % (ok, len(sub), 100 * ok / len(sub)) if sub else '-'

    normal = [r for r in rows if r['wrong_container'] != 'yes' and r['obstacle'] != 'yes' and 'missing' not in r['notes']]
    print('runs: %d   overall success: %s' % (len(rows), rate(rows)))
    print('normal runs (no injected fault): %s' % rate(normal))
    print('\nby collection point (all runs):')
    for p in sorted({r['collection_point'] for r in rows}):
        print('  %s  %s   (normal: %s)' % (p, rate([r for r in rows if r['collection_point'] == p]),
                                        rate([r for r in normal if r['collection_point'] == p])))
    ok = [r for r in rows if r['success'] == 'yes']
    if ok:
        for col, name in (('time_navigate_s', 'navigate to point'), ('time_verify_s', 'verify'),
                          ('time_transport_s', 'transport to storage')):
            vals = [float(r[col]) for r in ok]
            print('mean %-22s %.1f s  (min %.1f, max %.1f, n=%d successful runs)' %
                  (name + ':', statistics.mean(vals), min(vals), max(vals), len(vals)))
    causes = collections.Counter(r['failure_cause'] for r in rows if r['success'] != 'yes')
    if causes:
        print('\nfailures by cause:')
        for c, n in causes.most_common():
            print('  %2d x %s' % (n, c))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
