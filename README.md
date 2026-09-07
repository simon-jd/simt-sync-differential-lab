# SIMT Synchronization Differential Lab

An actual Vortex SimX/Verilator comparison focused on local-barrier semantics.
Explicit state invariants and an independent scoreboard diagnose failures on
both sides: cross-slot phase forwarding in RTL and premature repeated-generation
wait completion in SimX.

Read the [state contract](docs/semantics.md), [root-cause analysis](docs/root-cause.md),
and saved [evidence](results/evidence/). The existing upstream slot test is
attributed; the generation test, seeded block scoreboard, orchestration, and
analysis extend that coverage.

Measured results:

- Both baseline failures reproduced; both repaired kernels pass on both backends.
- Eight tests pass through Vortex's canonical regression entry point.
- Independent block test fails on original RTL and passes three reset/interleaving sweeps.

The local source changes are reviewable under `patches/`; additive tests live in
`overlays/`. Vendored source/toolchains and build outputs stay out of Git.
The Docker base is pinned, source/submodules are locked in `upstream.lock.json`,
and no physical GPU or FPGA is needed for processor simulation.

```bash
make test        # fast offline integrity and differential-evidence audit
make setup       # Linux Docker, Python 3.10+, git; fixed source + tools + build
make baseline    # separate original-model source and build
make reproduce   # expected original failures and fixed passes, both backends
make regression  # actual Vortex CI category: 8 cases, about 3 minutes measured
make synthesis   # SV2V + Yosys hierarchy/synthesis/asserted structural check
```

These setup and reproduction entry points have been executed locally. Allow
several GiB of downloads and tens of GiB of disk for source/toolchain/builds;
containers use four CPUs and a 16 GiB memory limit. Source and recursive
submodules are pinned, and the prebuilt toolchain tag is resolved to an immutable
commit. Apt dependencies are resolved at image-build time. Recorded binary
hashes identify the measured build, without promising compiler bit-reproducibility.

Run directories are immutable. To repeat `make reproduce`, use another prefix:
`bash scripts/container.sh python3 scripts/reproduce.py second-run`.
Build both model variants with the same default configuration before paired
replay; the canonical regression intentionally rebuilds two-core configurations,
so run `bash scripts/container.sh bash scripts/build.sh` before another default
replay after `make regression`.

The eight paired runs include two expected failures on original models.
The runner records those as `semantic_failure`; the orchestration succeeds only
when the expected failure/pass matrix is observed. A timeout or infrastructure
error is never accepted as a counterexample. The three fixed block seeds add
18,555 cycles, 50,316 checks and 312 resets; original RTL fails at cycle 8.

CI audits the checked-in evidence on each push. `make regression` and
`make synthesis` are the heavyweight live checks, distinct from that offline
audit. The [evidence index](results/evidence/index.json) selects records with
complete model-library hashes. Hashes detect divergence, not independent
third-party attestation; rerun the experiments to validate the claims yourself.

Read [resume/interview notes](docs/interview.md) and
[upstream attribution](THIRD_PARTY.md). No upstream contribution has been sent.

## Execution reliability update

The runner now bounds captured output, cancels whole process groups, and atomically
publishes terminal results. See the [review and validation evidence](docs/reliability-review.md)
and [dated hiring/technology rationale](docs/market-review-2026-09-06.md).
`make test` also re-parses the saved post-change live executions.

See the [follow-up completion audit](docs/completion-audit.md) for full live
matrix/regression replays, stricter identity gates and remaining hardware dependency.
