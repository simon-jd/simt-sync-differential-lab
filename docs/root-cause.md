# Two local-barrier failures, two independent oracles

Baseline: Vortex `bba80f8de208f867a173b587998ed5be9cefd1b4`, RV32,
one core, four warps, four threads; toolchain bundle v3.0.1. The study exercises
local barriers. Cross-core tests replicate independent local slots on each core.

| Test | Baseline SimX | Baseline RTL | Fixed SimX | Fixed RTL |
| --- | --- | --- | --- | --- |
| Existing slot-phase probe | pass | 256 missed flips | pass | pass |
| Seeded repeated-generation probe | 18 premature returns | pass | pass | pass |

The evidence is under `results/evidence/`. The generated kernels for each
baseline/fixed pair have the same binary hash. Semantic comparison uses token
parity, marker visibility and termination; cycles can differ between models.

## Slot forwarding

The earlier upstream `bar_slot_phase` kernel is credited to the Vortex
contributors and [PR #402](https://github.com/vortexgpgpu/vortex/pull/402).
It is reused as a known reproducer, not represented as an original discovery.

`VX_bar_unit` reads the next slot while completing a request for the previous
slot. Its phase working register selected the writeback whenever *any* slot
was being written. Two consecutive requests to different slots can therefore
use the first slot's new phase as the second slot's old phase. The asynchronous
token-return path already qualified forwarding with address equality.

The one-line fix applies that same `is_rdw_hazard` condition to the working
phase register. Same-slot dependencies still forward; different-slot reads
retain their own state. No delay bubble or workload-specific workaround is used.

An independent block-level scoreboard checks every observed phase and every
release mask. It fails at cycle 8 on an untouched baseline checkout and passes
the fixed design. This ties the system-level kernel symptom to the slot pipeline
and adds reset coverage that the older kernel does not exercise.

## Generation/token comparison

SimX stores a monotonically incrementing generation but `BAR.ARRIVE` returns
only its low bit. `BarrierUnit::wait` compared the unmasked generation against
that token. At generation 2, a waiter with token 0 therefore continued even
though its generation had not completed. A reference model is not automatically
correct: in this case processor RTL obeyed the explicit barrier invariant.

The new `bar_generation` kernel delays the last warp using a deterministic
xorshift-derived delay. That warp publishes a marker and fences before its
arrival. Other warps must not read the marker until the barrier completes.
A separate rendezvous prevents marker reuse across iterations. The first two
generations succeed; in eight iterations, the next six fail on each of three
early warps: **18 failures**, with first expected/observed marker `(3, 2)`.

The minimal fix compares generation parity against token parity. It preserves
the full generation for diagnostics, changes no event/count state, and obeys
the same one-bit token lifetime contract as RTL. The fixed test passes on both
backends without changing the kernel or adding a timing workaround.

## Regression and scope

`bar_generation` and the existing slot test are added to
`tests/regression/Makefile`. The `sync_semantics` YAML category is discovered by
the current `ci/regression.sh --test sync_semantics` entry point. Eight tests
passed, covering default and two-core/two-warp configurations on both backends.
The block test is wired into `hw/unittest/Makefile`; seeds 1, 42 and 2026 execute
18,555 cycles, 50,316 invariant checks and 312 resets. Counts quantify executed
checks; the contract in `semantics.md` states what those checks actually prove.

The contract excludes stale tokens older than one generation, duplicate or
missing arrivals, variable participant counts within a generation, async
transaction events, and global cluster barriers. These are not silently assumed
correct. Processor rtlsim bypasses the AFU; FPGA timing and complete XRT/AFU
integration are outside the evidence.

The primary `replay2-baseline-*` records come from a separately rebuilt baseline
source tree and hash both loaded model libraries, driver wrappers, generated
configuration, and kernels. The baseline and fixed kernels are byte-identical.
Earlier exploratory recordings remain local; the evidence index explicitly
selects the complete replay. Recorded binary hashes identify this build, not a
promise of bit-identical compiler output on every future host.

SV2V translation and Yosys `hierarchy -check; synth; check -assert` completed
with zero reported problems for the local-barrier wrapper. The generic mapped
netlist contains 1,295 cells including submodules. This is a structural smoke
check; no technology library, area target, clock constraint or physical timing
claim is attached to that number. See the preserved `yosys.log`.
