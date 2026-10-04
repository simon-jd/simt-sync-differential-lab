# SIMT Synchronization Differential Lab

A Vortex SimX/RTL differential study of per-slot barrier ownership and generation parity. An independent scoreboard defines the invariant; local patches, minimal counterexamples, seeded resets, and canonical regression evidence remain separately reviewable.

## Confirmed qualification results

These are the user-confirmed results from a separate cloud test run, recorded in the experience bank. The device, workload, timing round, and counting boundaries below remain part of each result. They are distinct from the CPU checks performed in this checkout; cloud-hosted testing does not imply production deployment.

- Repaired two local barrier-model defects against an independent scoreboard: SimX now decides tokens by generation parity and RTL forwarding only hits the same slot, while the slot reproducer keeps its upstream attribution; of the 8 paired kernel executions (2 kernels × baseline/fixed × SimX/RTL), the slot/RTL and generation/SimX baselines each produced one expected failure, the other two baseline groups were success controls, and all four fixed groups satisfied the participant-set and generation invariants.

- Ran 52,000 block-level invariant checks (16,400 / 17,400 / 18,200) over 18,555 RTL cycles in a fixed block configuration of 4 barrier slots, 4 participating warps and 3 consecutive generations, using seeds 1, 42 and 2026 (5,900 / 6,200 / 6,455 cycles) with unchanged kernels and identical inputs.

- Drove 312 reset events (104 per seed, rising-edge counted, 1-cycle pulses) as deliberate block state-machine stress, not kernel launches: each assertion clears the local scoreboard, revokes the unfinished generation and re-establishes a legal participant set after release, which accounts for the intentionally short average interval of about 59 cycles.

- Shrank both defect classes to minimal counterexamples: removing the slot comparison let a slot0 release wrongly update slot1 (still reproducing at 2 slots, 2 warps, 2 generations) and removing the parity comparison let a previous-generation token return early (still failing at 2 generations), while execution timeouts were classified as infrastructure failures rather than barrier counterexamples.

- Kept infrastructure errors out of the semantic results by hardening the differential runner with shared-directory admission, fresh event capture and process-group cleanup, and by rerunning the affected paired, canonical and structural checks.

## Implementation and reproduction

| Contract | Implementation |
|---|---|
| Paired execution | [scripts/reproduce.py](scripts/reproduce.py) |
| Independent scoreboard and local tests | [overlays](overlays) |
| Attributed local model changes | [patches](patches) |
| Saved model evidence | [results/evidence](results/evidence) |

Run each experiment into a fresh output directory to preserve earlier evidence.

```bash
make test
# CPU-hosted simulator/Verilator reproduction in the pinned container:
make setup
make baseline
make reproduce
make regression
make synthesis
```

Regression entry points: [tests/test_run_case.py](tests/test_run_case.py), [tests/test_evidence.py](tests/test_evidence.py), [tests/test_process_runner.py](tests/test_process_runner.py).

## Scope and evidence

The historical checked-in reset sweep has 50,316 checks; the confirmed external round has 52,000. Neither is a physical GPU/FPGA qualification.

- 312 is a count of block-level reset events (rising edges, 1-cycle pulses) in a small barrier testbench: 104 events per seed over 5,900 / 6,200 / 6,455 cycles, averaged about one every 59 cycles by design. Never present it as a full GPU or kernel launch count; pulse widths are stored separately and nothing here extrapolates to real hardware timing.

- Neither SimX nor RTL is a standalone correctness oracle: pass/fail comes from an independent scoreboard that stores per-slot phase and checks the participant-set and generation contract, and two deliberately broken model variants were used to prove the gate reports errors instead of passing everything.

- The participant set is only within the fixed block (4 slots, 4 warps, 3 generations); a reset terminates the current generation rather than completing synchronization for all participants, and cross-block residency, scheduling preemption and global progress were never in the state model.

- The minimal counterexamples only prove the specified slot and generation contract; do not upgrade them to arbitrary stale-token safety. Execution timeouts are infrastructure failures, not barrier counterexamples.

- The 52,000 invariant checks (16,400 / 17,400 / 18,200) supersede the earlier 50,316 slice; do not infer faults from the difference between rounds.

- The slot regression is attributed to upstream Vortex contributors; no claim is made that upstream accepted the local fixes or that anything was FPGA-verified. This is an AI-assisted personal project using local CPU-hosted simulators.

- Historical baseline replays retain 256 RTL missed-phase-flip executions and 18 SimX premature-return executions; the 8 kernel executions are 2 kernels × baseline/fixed × SimX/RTL.

The [previous README](README.historical.md) preserves earlier setup details, design discussion, and historical measurements. Its older counts, splits, versions, and timing cohorts must not be mixed with the confirmed round above. [Result provenance](docs/experience-bank-results.json) retains the confirmed bullet text; [checkout validation](docs/checkout-validation.md) records what was actually rerun here.
