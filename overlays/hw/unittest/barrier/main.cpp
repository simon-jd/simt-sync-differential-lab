#include "VVX_barrier_top.h"
#include <verilated.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>

struct Request {
  bool valid = false;
  unsigned slot = 0, warp = 0, count = 1, token = 0;
  bool arrive = true, sync = false;
};

struct Slot {
  unsigned generation = 0, arrivals = 0, waiters = 0;
};

class Bench {
public:
  VVX_barrier_top dut;
  std::array<Slot, 32> slots{};
  Request pending;
  unsigned cycle = 0, checks = 0, resets = 0;
  FILE* trace;

  explicit Bench(FILE* trace_file) : trace(trace_file) {}

  void check(bool ok, const char* invariant) {
    ++checks;
    if (!ok) {
      std::fprintf(stderr, "cycle=%u invariant=%s\n", cycle, invariant);
      throw std::runtime_error(invariant);
    }
  }

  void step(Request next = {}, bool reset = false) {
    unsigned released = 0;
    bool release = false;
    if (reset) {
      slots = {};
      ++resets;
    } else if (pending.valid) {
      auto& slot = slots.at(pending.slot);
      if (pending.arrive) {
        if (pending.sync) {
          slot.waiters |= 1u << pending.warp;
        }
        if (++slot.arrivals == pending.count) {
          slot.arrivals = 0;
          ++slot.generation;
          released = slot.waiters;
          slot.waiters = 0;
          release = true;
        }
      } else if ((slot.generation & 1u) == pending.token) {
        slot.waiters |= 1u << pending.warp;
      } else {
        release = true;
        released = 1u << pending.warp;
      }
    }
    dut.clk = 0;
    dut.reset = reset;
    dut.req_valid = pending.valid;
    dut.req_wid = pending.warp;
    dut.is_arrive = pending.arrive;
    dut.is_sync = pending.sync;
    dut.phase = pending.token;
    dut.size_m1 = pending.count - 1;
    dut.read_addr = next.slot;
    dut.eval();
    const unsigned expected_phase = slots.at(next.slot).generation & 1u;
    std::fprintf(trace, "%u,%u,%u,%u,%u,%u,%u,%u,%u\n", cycle,
                 reset, pending.valid, pending.slot, next.slot,
                 expected_phase, unsigned(dut.read_phase), release, released);
    if (!reset) {
      check(dut.read_phase == expected_phase, "slot phase / forwarding");
    }
    dut.clk = 1;
    dut.eval();
    check(bool(dut.unlock_valid) == release, "wait release timing");
    if (release) {
      check(dut.unlock_mask == released, "exact waiter mask");
    }
    pending = reset ? Request{} : next;
    ++cycle;
  }

  void issue(Request request) {
    step(request);
    step();
  }
};

static uint32_t random_next(uint32_t& state) {
  state ^= state << 13;
  state ^= state >> 17;
  state ^= state << 5;
  return state;
}

int main(int argc, char** argv) {
  Verilated::commandArgs(argc, argv);
  uint32_t state = argc > 1 ? std::strtoul(argv[1], nullptr, 0) : 1;
  const uint32_t seed = state;
  FILE* trace = std::fopen("barrier-events.csv", "w");
  if (!trace || state == 0) {
    return 2;
  }
  std::fprintf(trace, "cycle,reset,pending_valid,pending_slot,read_slot,expected_phase,rtl_phase,release,mask\n");
  try {
    Bench bench(trace);
    bench.step({}, true);
    bench.step({}, true);
    for (unsigned i = 0; i < 4096; ++i) {
      const unsigned slot = random_next(state) % 32;
      bench.step({true, slot, random_next(state) % 4, 1, 0, true, false});
      if ((random_next(state) & 63) == 0) {
        // Reset can discard an in-flight request and every prior slot generation.
        bench.step({}, true);
      }
    }
    bench.step();
    for (unsigned i = 0; i < 256; ++i) {
      const unsigned slot = random_next(state) % 32;
      const unsigned token = bench.slots[slot].generation & 1u;
      bench.issue({true, slot, 0, 2, 0, true, false});
      bench.issue({true, slot, 0, 2, token, false, false});
      if ((i & 7) == 0) {
        // Reset while a warp is waiting: its stale wait mask must not survive.
        bench.step({}, true);
        bench.issue({true, slot, 1, 1, 0, true, false});
      } else {
        bench.issue({true, slot, 1, 2, 0, true, false});
        bench.issue({true, slot, 1, 2, token, false, false});
      }
    }
    std::printf("seed=%u cycles=%u checks=%u resets=%u\n", seed,
                bench.cycle, bench.checks, bench.resets);
    std::puts("PASSED!");
  } catch (const std::exception& error) {
    std::fprintf(stderr, "seed=%u FAILED: %s\n", seed, error.what());
    std::fclose(trace);
    return 1;
  }
  std::fclose(trace);
  return 0;
}
