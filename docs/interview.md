# Resume and interview evidence

Use these bullets after reproducing the experiments and explaining the state
transitions independently. This is processor simulation and local RTL checking.

**GPU functional modeling / design verification**

- Developed a seeded SIMT barrier-generation kernel and independent RTL
  scoreboard; reproduced 18 premature SimX returns and an attributed upstream
  RTL slot-phase failure on a pinned Vortex revision.
- Diagnosed generation/token-width and cross-slot forwarding errors, implemented
  two one-line model repairs, and verified unchanged kernels on both SimX and
  Verilator backends with eight canonical regression passes.
- Exercised 18,555 RTL cycles, 50,316 invariant checks and 312 resets across
  three deterministic seeds; preserved failing baseline traces and completed
  a focused SV2V/Yosys structural synthesis check.

Evidence: [root causes](root-cause.md), [state contract](semantics.md),
[minimal patches](../patches/), [raw records](../results/evidence/).

Interview checkpoints:

- Draw two adjacent slot requests through the read/modify/write pipeline.
  Identify precisely when bypass data belongs to the requested address.
- Derive why generation 2 and one-bit token 0 must compare equal before the
  final arrival; distinguish current-generation correctness from stale-token ABA.
- Explain the marker/fence ordering, last-warp delay and separate rendezvous.
- Explain which outputs the scoreboard compares before and after a clock edge,
  and why pre-edge phase comparison is disabled while reset is asserted.
- Explain why neither SimX nor RTL is always an oracle and why cycle counts
  need not match for semantic differential testing.
- State the uncovered cases: invalid participant protocols, async events,
  global barriers, full AFU/XRT integration and physical implementation timing.

The slot-phase reproducer belongs to upstream contributors (PR #402); it is not
an original discovery. The generation probe, scoreboard, focused local fixes
and reproducible evidence are this project's contribution. No upstream PR has
been submitted or accepted for this work.
