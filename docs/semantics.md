# Local barrier contract and comparison boundary

Scope: local barrier slots, independently owned by each core and CTA context.
Multiple cores exercise slot isolation; cluster/global barrier correctness is
outside this local-barrier study. Both actual SimX and actual processor RTL are
execution subjects. A small mathematical specification is an independent oracle.

For slot `s`, track `(generation, arrivals, waiters, pending_events)` with a fixed
participant count `N >= 1`. The architectural token is `generation mod 2`.

| Event | State transition | Observable consequence |
| --- | --- | --- |
| Reset | all slots return to generation 0, count 0, empty waiters/events | old waits do not survive reset |
| Arrive | return old parity; increment arrivals modulo N | one contribution per participant per generation |
| Final arrive, no pending events | advance generation, clear waiters | release exactly this slot's waiters |
| Wait(token), same parity | add caller to waiters | caller cannot execute beyond wait yet |
| Wait(token), different parity | state unchanged | caller may continue immediately |
| Other slot update | this slot unchanged | no phase/count/waiter contamination |

Event-attachment semantics are relevant context; randomized tests of this v1
local-arrive/wait contract will keep pending events at zero. Do not infer
transaction-engine verification from these tests.

One-bit tokens require that a waiter not lag by two completed generations (ABA).
Test programs obey this lifetime restriction and reuse a slot only after all
participants finish the current iteration. No claim is made for invalid programs
with duplicate arrival, changed participant counts, or stale two-generation tokens.

The comparison projects SimX generation onto its low bit. Returned tokens,
progress ordering, payload visibility after an explicit fence, slot isolation,
reset behavior, and exit status are semantic observables. SimX/RTL cycle counts
are recorded separately and are not required to be identical by this contract.

## Hand-worked sequence

Two warps, slot 0, no pending events:

1. Complete generations 0 and 1. State is `(generation=2, arrivals=0)`;
   architectural parity is 0.
2. Warp 0 arrives. It receives token 0; arrivals becomes 1.
3. Warp 0 waits on token 0. Since current parity is also 0, it must block.
4. Warp 1 publishes marker 3, fences, then arrives. Generation becomes 3.
5. Warp 0 resumes and must see marker 3.

Comparing the integer 2 against token 0 at step 3 releases warp 0 too early.
The seeded `bar_generation` kernel exercises this sequence with a delayed final
warp and checks the marker before a separate rendezvous reuses it.

```mermaid
sequenceDiagram
  participant W0 as Warp 0
  participant B as Slot 0 (generation 2 / parity 0)
  participant W1 as Delayed warp
  W0->>B: arrive -> token 0
  W0->>B: wait(0)
  Note over W0,B: Must remain blocked
  W1->>W1: publish marker 3; fence
  W1->>B: final arrive
  Note over B: generation 3 / parity 1
  B-->>W0: resume
  W0->>W0: verify marker == 3
```

Source inspection suggests two distinct candidates: the published cross-slot
forwarding issue and a SimX full-generation/token comparison. Neither is called
a confirmed result until real executions and before/after evidence are saved.
