# Engineering and hiring review — 2026-09-06

Sources checked on 2026-09-06 America/Los_Angeles (2026-09-07 UTC).
The sample is targeted, small, and not an estimate of market prevalence.
Official publication metadata is saved in `../results/review/job-dates.json`; a crawler timestamp
is not a posting date. No job application or recruiter contact was made.

| Official role | Posting date | Relevant signal and fit |
| --- | --- | --- |
| [Zip, New Grad 2027](https://jobs.ashbyhq.com/zip/df6eb1ee-b360-46fe-b23f-658626ec59ea) | 2026-08-25, official Ashby API | Reliability, maintainability, APIs; Dec 2026–Jun 2027 graduation window. |
| [Scale AI, New Grad](https://job-boards.greenhouse.io/scaleai/jobs/4730836005) | 2026-09-04, official Greenhouse API | Testable evaluation tooling and data systems; Fall 2026/Spring 2027 graduation. |
| [Cerebras, ML Systems Integration](https://jobs.ashbyhq.com/cerebras/c35a389c-807e-45fb-bfda-03f6b1361871) | 2026-09-03, official Ashby API | Python/C++, Linux process/concurrency fundamentals, diagnostics; no numerical experience minimum stated. Hardware bring-up remains a stretch. |
| [AWS Data Services, Fall SDE Intern](https://www.amazon.jobs/en/jobs/10412530/software-development-engineer-intern-aws-data-services-fall-2026-us) | Original date unavailable; page checked today | Fault tolerance, CI/CD, operational debugging. Graduation fits; immediate start and full-time availability are unconfirmed. |

Repeated signals in this sample: reliability (Zip/AWS), diagnostic discipline
(AWS/Cerebras), and test/validation tooling (Scale/Cerebras). Go, GraphQL, AWS,
MongoDB, and hardware bring-up are role-specific preferences, not universal
requirements. AI product activity does not establish demand for an arbitrary
new framework. The inference for these projects is to improve execution and
measurement trustworthiness while retaining their systems focus.

The indexed [Cerebras Integration & Quality New Grad](https://jobs.ashbyhq.com/cerebras/05fd05ea-b515-4c26-851e-b3882dfba154)
was absent from the current official board, so it is historical context only.
[Thumbtack AI/ML Infrastructure](https://careers.thumbtack.com/jobs/3efb1a7b-cfaf-475a-86a9-abff37581b4b)
requests 1–3 years; its official page includes a filled-role notice. Its status
is uncertain and it is excluded from current-vacancy evidence. Sponsorship and
employer-specific eligibility were not confirmed for these samples.

Portfolio decision: existing backend projects already demonstrate APIs, durable
workflows, databases and deployment. A and C add performance qualification;
B adds concurrency semantics and differential debugging. These are supporting
projects for general Backend/Cloud roles and stronger technical matches for
systems validation or ML infrastructure integration. They do not establish
production operations or actual ML training/serving experience.

## Dependency decision

[Vortex v2.3](https://github.com/vortexgpgpu/vortex/releases/tag/v2.3)
(2026-04-25) is the latest non-prerelease in the API sample;
[v3.0](https://github.com/vortexgpgpu/vortex/releases/tag/v3.0) is a prerelease.
Release notes describe simulator/TCU and floating-point integration changes.
The current immutable master revision supports the local-barrier API used by
this regression. Moving to v2.3 would be a downgrade requiring source/test
adaptation, and moving toolchains risks invalidating the paired comparison.
The pinned toolchain v3.0.1 commit is separate from a stable processor release.
Keep both source and tools pinned for this change.

All three upstream repositories were active and not archived in the official
GitHub API check. No simulator/framework upgrade or new Python dependency is
needed for the observed process-lifecycle defects. The runner uses standard
POSIX facilities supported in the existing Python 3.10/3.12 containers.
