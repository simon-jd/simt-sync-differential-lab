# Attribution and licensing

This repository uses Apache-2.0 (see `LICENSE`), consistent with Vortex.
Vortex source, generated RTL evidence and focused patches retain upstream
copyrights. The source and recursive submodule versions are in `upstream.lock.json`.
Downloaded toolchains and dependencies retain their own upstream licenses.

The existing `bar_slot_phase` kernel was contributed upstream by Runjia Chen in
[PR #402](https://github.com/vortexgpgpu/vortex/pull/402). Its earlier failure case
is reused and explicitly credited. The `bar_generation` host launcher adapts
that scaffold; the seeded repeated-generation kernel and block scoreboard are
new project tests. Cross-slot phase behavior was already discussed upstream;
the local repair and independent evidence are not presented as first discovery.

The simulator, processor RTL, compiler, Verilator, SV2V and Yosys are upstream
work. This project's contribution is the scoped semantic contract, additional
tests, two focused local repairs, orchestration and measured analysis. No
upstream acceptance, FPGA deployment or NVIDIA hardware validation is claimed.
