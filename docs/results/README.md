# Results — Repeated Simulation Runs

How to log and summarise the repeated test runs described in `docs/results/test_plan.md`.

## Where results actually come from

The task manager writes one row per task run to `~/hcw_ws/results/runs.csv` on the machine the
tests are run on. After a test session, copy the rows you want to keep into a dated CSV in this
folder using the same columns as `run_log_template.csv` below.

The Week 4 results are already recorded this way:
- `docs/results/runs_all_sessions.csv` — every logged run across all sessions
- `docs/results/runs_final_settings.csv` — only the runs under the final, working settings
  (30 normal tasks, 6 fault cases; see `docs/09_Week4_Results.md` for the full write-up)

`run_log_template.csv` stays as a header-only starting point for any further test sessions.

## Columns

Each row is one task run.

| Column | Meaning |
|---|---|
| `run_id` | A unique id for this run (for example, an incrementing number or a timestamp) |
| `date` | The date the run was performed |
| `collection_point` | Which point the task targeted: A, B or C |
| `wrong_container` | `yes` if this run deliberately used a wrong container, otherwise `no` |
| `obstacle` | `yes` if this run deliberately included a blocking obstacle, otherwise `no` |
| `success` | `yes` if the task reported `COMPLETED`, `no` if it reported `FAILED` or `REJECTED` |
| `time_navigate_s` | Time in seconds spent navigating to the collection point |
| `time_verify_s` | Time in seconds spent verifying the container at the collection point |
| `time_transport_s` | Time in seconds spent navigating from the collection point to storage |
| `failure_cause` | The exact cause reported by the task manager if the run failed or was rejected, otherwise blank |
| `notes` | Anything else worth recording about this specific run |

## Computing the task success rate

For any group of runs (for example, all runs at a given collection point, or all runs overall),
the success rate is: the number of rows with `success = yes`, divided by the total number of
rows in the group. Expressed as a percentage, multiply by 100.

## Success rate per collection point

From `docs/results/runs_final_settings.csv` (final settings, see `docs/09_Week4_Results.md`):

| Collection point | Runs | Successes | Success rate |
|---|---|---|---|
| A | 18 | 18 | 100% |
| B | 6 | 6 | 100% |
| C | 6 | 6 | 100% |
| Overall | 30 | 30 | 100% |

Fault cases (missing/wrong container) are handled separately: 6 of 6 correctly FAILED with the
right cause, see `docs/09_Week4_Results.md` section 3. A 100% success rate on 30 runs does not
mean the system never fails; see the "things you must not read into these numbers" section of
that doc for the honest statistical caveat (about 88% or higher at 95% confidence, not "never
fails").
