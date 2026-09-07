#include <vx_spawn2.h>
#include <vx_intrinsics.h>
#include <vx_barrier.h>
#include "common.h"

static uint32_t mix(uint32_t x) {
  x ^= x << 13;
  x ^= x >> 17;
  x ^= x << 5;
  return x;
}

__kernel void kernel_main(kernel_arg_t* __UNIFORM__ arg) {
  auto marker = reinterpret_cast<volatile uint32_t*>(__local_mem());
  auto errors_out = reinterpret_cast<uint32_t*>(arg->err_addr);
  auto expected_out = reinterpret_cast<uint32_t*>(arg->pre_addr);
  auto observed_out = reinterpret_cast<uint32_t*>(arg->post_addr);
  const uint32_t wid = vx_warp_id();
  const uint32_t tid = vx_thread_id();
  const uint32_t cid = vx_core_id();
  vortex::barrier probe(0);
  vortex::barrier gate(2);
  uint32_t errors = 0, first_expected = 0, first_observed = 0;

  if (wid == 0 && tid == 0) {
    marker[0] = 0;
  }
  vx_fence();
  gate.arrive_and_wait();

  for (uint32_t round = 0; round < arg->rounds; ++round) {
    const uint32_t expected = round + 1;
    if (wid + 1 == arg->num_warps) {
      const uint32_t delay = 128 + (mix(arg->seed ^ round ^ (cid << 16)) & 127);
      for (uint32_t i = 0; i < delay; ++i) {
        __asm__ volatile ("nop" ::: "memory");
      }
      if (tid == 0) {
        marker[0] = expected;
      }
      vx_fence();
    }

    const uint32_t token = probe.arrive();
    probe.wait(token);
    vx_fence();
    const uint32_t observed = marker[0];
    if (wid + 1 < arg->num_warps && observed != expected) {
      if (errors == 0) {
        first_expected = expected;
        first_observed = observed;
      }
      ++errors;
    }
    // Every warp finishes its observation before the marker is reused.
    gate.arrive_and_wait();
  }

  if (tid == 0) {
    const uint32_t index = cid * arg->num_warps + wid;
    errors_out[index] = errors;
    expected_out[index] = first_expected;
    observed_out[index] = first_observed;
  }
}
