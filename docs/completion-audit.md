# Completion audit and follow-up — 2026-09-06 Pacific

This follows the earlier review; its raw evidence remains immutable. A new
requirement audit reproduced additional defects before editing:
`results/completion/before-gates.json`. Those probes used controlled processes
and modifications to copies of real saved artifacts, not fabricated hardware data.

## Changes

SIGINT/SIGTERM now stops the whole A/C batch after persisting the current
execution outcome, returning 128 + signal instead of starting the next case.
The shared process runner retains cancellation arriving during final cleanup
and restores signal handlers even when cleanup raises. A real-signal regression
checks the batch boundary, and a focused regression checks cleanup timing.

Canonical sync_semantics regression was executed again after configure: eight cases passed. The default configuration was then rebuilt, paired counterexamples/repairs were replayed, and SV2V/Yosys structural checks were repeated. The synthesized input is retained and hash-checked.

A/C fault commands accept `--run-id` and default to a fresh identifier, so they
can be executed repeatedly without overwriting earlier failure evidence. C's
`--baseline-run-id` selects the source matrix for measurement fault checks.

## Verified scope

Eight new paired system runs and four RTL unit runs preserve all expected outcomes. Three fixed seeds again total 18,555 cycles, 50,316 checks and 312 resets. Eight canonical cases and the structural synthesis check pass.

`make test` now passes 17 tests plus the original, review, and full-completion
evidence audits. Eleven lifecycle/filesystem cases are shared copies across
ABC and must not be summed as distinct scenario coverage. The actual container
runtime was also tested. Host and container transcripts are stored separately.
`results/completion/evidence/index.json` identifies new raw outputs;
`scripts/completion_evidence.py verify` reparses them and recomputes acceptance.
Original matrix logs and normalized data were not replaced or retuned.

For a new full A/C matrix, supply a fresh `--run-id`. For B, provide a fresh
prefix to `scripts/reproduce.py`; rebuild default configuration after canonical
regression before paired replay. `completion_evidence.py` deliberately names
this archived completion run; its `pack` operation refuses an existing archive.

## Completion boundary

The previously deferred full local parameter matrices, affected Vortex canonical
regression and focused synthesis checks have now actually run. This does not
mean all possible workloads, full AFU/XRT integration, physical FPGA timing,
production SLOs or cloud application deployment have been verified. Those were
not claimed features. Hosted CI remains an offline audit plus process tests.

A hardware calibration remains incomplete: local hardware is RTX 4090, while
this suite uses Volta sm_70. Its historical V100 reference is CUDA 11.2/Rodinia
3.1 and the traces are CUDA 11.0/Rodinia 2.0 without matching executable hashes.
`results/completion/calibration-readiness.json` in A records the checked blocker.
No error table is manufactured from those incompatible populations. The broad
follow-up goal is not marked achieved while that requested completeness remains
unproven; a matching machine/capture was requested from the user.
