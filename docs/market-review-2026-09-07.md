# Hiring and ecosystem review — 2026-09-07

## Official hiring sample

Checked 2026-09-07. This is a small purposive sample, not a labor-market survey.
The two explicit new-grad windows cover Spring 2027 graduates.
Sponsorship availability was not established from these pages.

| Official posting | Publication evidence | Relevant requirements and fit |
| --- | --- | --- |
| [Zip — Software Engineer, New Grad (2027 Start)](https://jobs.ashbyhq.com/zip/df6eb1ee-b360-46fe-b23f-658626ec59ea) | Official API snapshot read on Sep 6: Aug 25, 2026; live page read in browser Sep 7 | Dec 2026–Jun 2027 BS/MS; reliable products, maintainable code, APIs. Python/TS/React/GraphQL are Zip's stack preferences. |
| [Scale — Software Engineer, New Grad](https://job-boards.greenhouse.io/scaleai/jobs/4730836005) | Official Greenhouse API `first_published` Sep 4, 2026; API and page checked Sep 7 | Fall 2026/Spring 2027 graduation; product/API experience, large-volume data systems, evaluation infrastructure. Python/TS/React/MongoDB are role-specific preferences. |
| [Cerebras — ML Systems Integration Engineer](https://jobs.ashbyhq.com/cerebras/c35a389c-807e-45fb-bfda-03f6b1361871) | Official API snapshot read Sep 6: Sep 3, 2026; live page read in browser Sep 7 | Sunnyvale/Toronto; BS/MS and no numerical experience floor stated, but not labeled new-grad. Linux, Python/C++, processes/memory/concurrency, system debugging, validation automation and telemetry. Adjacent systems target, not confirmed entry-level eligibility. |

Ashby posting APIs returned HTTP 403 on Sep 7. Live browser reads confirmed the
Zip and Cerebras descriptions; publication dates above remain the Sep 6 official
metadata snapshot, not newly retrieved dates. Research metadata is retained in the local portfolio review workspace. No application
was submitted. Pylon's JS-only indexed result was not used as a verified sample.

Reliability/quality recur in all three descriptions; Python recurs in all three;
Zip and Scale explicitly mention APIs, while Scale and Cerebras emphasize
validation infrastructure. Cerebras uniquely emphasizes hardware/software bring-up.
The priority choice is an engineering inference from that sample and the portfolio,
not a claim that most North American employers demand these exact tools. AI product
language and upstream Hopper features do not establish demand for a new GPU model.

## Official ecosystem and migration review

GitHub repository/release APIs checked Sep 7; all three repositories are unarchived
and show recent maintenance. Source commits remain pinned, with no dependency
upgrade in this change.

- [Accel-Sim v2.0.0](https://github.com/accel-sim/accel-sim-framework/releases/tag/v2.0.0),
  stable, Aug 25, 2026. Release migration notes require matching GPGPU-Sim for Hopper
  and explain compressed `.tracez` versus legacy `--text` traces. The release tag
  was re-cut for documentation; exact commits remain the reproducibility anchor.
  Existing pinned Volta experiments already execute successfully. Switching device,
  trace generation and profiling would require fresh captures, independent inventory
  and a full matrix. No benefit to the current admission/validation contract justifies
  that cost. Upstream performance claims are not measurements of this project.
- [Vortex v3.0](https://github.com/vortexgpgpu/vortex/releases/tag/v3.0), June 9, 2026,
  is marked **prerelease** by GitHub; [v2.3](https://github.com/vortexgpgpu/vortex/releases/tag/v2.3),
  April 25, is the latest stable entry reviewed. v3 describes asynchronous barrier
  semantics, `vortex2.h`, configuration namespace/layout and toolchain changes.
  B's pinned master source targets those barrier semantics with its matched toolchain.
  A release number is not a drop-in replacement: upgrading/reverting would require
  new paired builds, canonical regression and structural checks. Retain the tested pin.
- [gem5 v25.1.0.1](https://github.com/gem5/gem5/releases/tag/v25.1.0.1), stable,
  April 21, 2026, fixes RISC-V checkpointing and Arm-host build behavior. Neither
  addresses the current X86 TimingSimpleCPU workload. The
  [v25.1 release notes](https://github.com/gem5/gem5/releases/tag/v25.1.0.0)
  document user-facing walk-cache and statistics changes; migrating the current
  develop pin would need rebuild, configuration review and all 25 experiments.
  No current failure or measured benefit warrants changing the baseline.


This portfolio project supplies supporting systems evidence. Existing backend
projects cover web/API deployment; this maintenance preserves the distinct
simulator validation scope. See [current test evidence](../results/maintenance-20260907/verification.json).
