"""Reproduce the numbers and the figure of the report from the run log.

    python scripts/analyze_runs.py            (run from the report folder; needs matplotlib for the figure)

Input : data/runs_56_128.csv   (73 logged runs: 67 normal tasks and 6 staged faults; 25 Oct and 7-8 Nov 2026)
Output: printed statistics, and figures/fig_times.pdf
"""
import csv
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'runs_56_128.csv'), encoding='utf-8')))
ok = [r for r in rows if r['success'] == 'yes']
bad = [r for r in rows if r['success'] != 'yes']
print('runs: %d  completed: %d  refused/failed: %d' % (len(rows), len(ok), len(bad)))
for r in bad:
    print('  fault run %s, room %s: %s' % (r['run_id'], r['collection_point'], r['failure_cause']))

for room in 'ABC':
    nav = [float(r['time_navigate_s']) for r in ok if r['collection_point'] == room]
    tr = [float(r['time_transport_s']) for r in ok if r['collection_point'] == room]
    print('room %s: n=%d  navigate median %.1f s (range %.1f-%.1f)  carry median %.1f s' %
          (room, len(nav), statistics.median(nav), min(nav), max(nav), statistics.median(tr)))

batch = [r for r in ok if 56 <= int(r['run_id']) <= 85]
tot = [float(r['time_navigate_s']) + float(r['time_verify_s']) + float(r['time_transport_s']) for r in batch]
print('30-task batch (runs 56-85), request to report: mean %.1f  median %.1f  min %.1f  max %.1f' %
      (statistics.mean(tot), statistics.median(tot), min(tot), max(tot)))

a_pre = [float(r['time_navigate_s']) for r in ok if r['collection_point'] == 'A' and int(r['run_id']) < 121]
a_post = [float(r['time_navigate_s']) for r in ok if r['collection_point'] == 'A' and int(r['run_id']) >= 121]
print('room A before the heading-tolerance change: %d trips, %d slow (>60 s); after: %s' %
      (len(a_pre), sum(1 for x in a_pre if x > 60), a_post))

n = len(ok)
print('success rate, %d/%d: exact one-sided 95%% lower bound %.3f ; failure-rate upper bound (rule of three) %.3f' % (n, n, 0.05 ** (1 / n), 3 / n))
print('faults 6/6: exact one-sided 95%% lower bound %.3f' % (0.05 ** (1 / 6)))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.9))
    cols = {'A': '#2E6BFF', 'B': '#1FA85A', 'C': '#F08A00'}
    for ax, key, title in ((axes[0], 'time_navigate_s', 'Drive to room'), (axes[1], 'time_transport_s', 'Carry to storage')):
        for i, room in enumerate('ABC'):
            ys = [float(r[key]) for r in ok if r['collection_point'] == room]
            xs = [i + (j % 7 - 3) * 0.05 for j in range(len(ys))]
            ax.scatter(xs, ys, s=5, color=cols[room], alpha=0.8, linewidths=0)
            ax.hlines(statistics.median(ys), i - 0.3, i + 0.3, color='black', linewidth=0.8)
        ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['A', 'B', 'C'], fontsize=6)
        ax.set_title(title, fontsize=6.5); ax.tick_params(axis='y', labelsize=6)
        ax.set_xlabel('Collection room', fontsize=6)
    axes[0].set_ylabel('Time (s)', fontsize=6.5)
    plt.tight_layout(pad=0.4)
    out = os.path.join(ROOT, 'figures', 'fig_times.pdf')
    plt.savefig(out)
    print('figure written:', out)
except ImportError:
    print('matplotlib not installed: figure skipped')
