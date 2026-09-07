# Execution reliability review — 2026-09-06

This records the first review. The [follow-up audit](completion-audit.md) closes
its deferred full local reruns and adds further regression gates.

## Decision and acceptance

The [dated role/ecosystem review](market-review-2026-09-06.md) supports these
bounded changes to the existing experiment system:

| Priority | Engineering value | Acceptance |
| --- | --- | --- |
| P0: process lifecycle | Stop same-group descendants, classify cancellation/start failure, bound captured stdout/stderr | Real fork, TERM-resistant child, SIGTERM cancellation, missing executable, output flood tests |
| P0: result integrity | Complete JSON publication and project-specific admission/validation | Concurrent readers, invalid JSON, adapter failure cases |
| P1: reproducibility | Re-run pinned real backends without overwriting original evidence | Raw outputs re-parsed and compared against the previous baseline |

The baseline was reviewed before editing. `results/review/before-faults.json`
records controlled host-process probes against the original A/B adapters:
unknown A selection returned success without work; a timeout left a runnable
TERM-resistant child after its leader exited; missing B executable raised
without result.json; stale B events were copied into a new run. These probes
used Python fixtures, not simulated GPU measurements. Shared timeout logic in
all three projects had the leader-only cleanup weakness. The old C code also
assigned counters before final address validation; its new regression gate is
explicitly labeled below. Original experiment data was preserved.

## Implemented contract

`process_runner.py` starts each executable in its own POSIX session. It streams
combined stdout/stderr into an 8 MiB bounded file instead of accumulating
unbounded output. On timeout, cancellation, overflow, or a leader exiting with
remaining descendants, cleanup sends TERM to the group and escalates to KILL
after 250 ms even if the leader has already exited. Records expose exit status,
process-group ID, output bytes/limit, cancellation signal and cleanup escalation.
Launch errors are terminal infrastructure outcomes. Main-thread SIGINT/SIGTERM
handling restores the caller's previous handlers after each execution.

Result JSON uses a same-directory temporary file, flush/fsync and atomic replace.
Readers observe complete old/new documents; invalid non-finite values are
rejected before replacement. Fresh case directories remain fail-closed.

Serialize access to shared build/test outputs with a cooperative file lock. Preserve prior event CSV separately; only newly produced events count. Persist preflight/launch errors, and require diagnostic patterns for semantic failures.

This is a local experiment runner, with bounded captured logs, not a distributed
scheduler. A simulator can still write other files directly; the log limit does
not cap total artifact disk usage. SIGKILL of the executor, host loss, disk I/O
failure, and descendants deliberately leaving their process group are outside
the guarantee. Such interruption can leave a reserved directory without a final
record; there is no automatic resume. File locks only coordinate cooperating B
executors and do not lock out an independently launched compiler. Atomic file
replacement is not a multi-file transaction or a security sandbox.

## Verification

`make test` passed 16 tests on the local host, plus the original evidence
audit and new `scripts/review_evidence.py` audit. Ten lifecycle/atomic-publication
tests are identical copies across A/B/C; do not market them as 30 unique cases.
B's Python 3.10 and C's Python 3.12 container tests also passed. Host-process
fault tests and offline artifact audits are distinct from live simulation.

8 paired system executions reproduce both original counterexamples and all fixed passes. Four block executions reproduce the original failure and three fixed seeds: 18,555 cycles, 50,316 checks, 312 resets.

Raw post-change output is compressed in `results/review/live/`; its hash index
and reparsing verifier are committed. `results/review/verification.json` is the
computed summary. `results/review/environment.json` records environment and code
identity. The original evidence audit still covers the complete historical
matrix. This review replays baseline/differential cases, not every parameter
sweep or the heavyweight synthesis/regression builds, whose source was unchanged.
No throughput, wall-time improvement, production reliability percentage, or
hardware accuracy improvement is claimed. Host timings from concurrent local
runs are diagnostic values and not a before/after benchmark.

```bash
make test
bash scripts/container.sh python3 scripts/reproduce.py YOUR_NEW_ID
```

Each replay requires a new identifier. Historical `make report` remains scoped
to the original canonical matrix; a new namespace does not silently replace it.
For C, the deliberate live negative check is
`bash scripts/container.sh python3 scripts/check_mapping_failure.py YOUR_FAULT_ID`.
It is validation evidence and cannot enter a successful measurement population.

The code and evidence were developed with AI assistance. Reviewers should use
the tests, model patches, traces, and explicit limitations to evaluate the work;
no independent authorship, upstream acceptance, cloud application deployment,
or production operation is implied.
