#pragma once
#include <stdint.h>

struct kernel_arg_t {
  uint32_t num_cores;
  uint32_t num_warps;
  uint32_t rounds;
  uint32_t seed;
  uint64_t err_addr;
  uint64_t pre_addr;
  uint64_t post_addr;
};
