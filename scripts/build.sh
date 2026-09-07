#!/usr/bin/env bash
set -euo pipefail
source_name=vortex
build_name=build32
if [ "${1:-}" = --baseline ]; then
  source_name=vortex-baseline
  build_name=build-baseline32
fi
mkdir -p "$build_name"
cd "$build_name"
"../vendor/$source_name/configure" --xlen=32 --tooldir=/workspace/tools
tool_commit=$(python3 -c 'import json; print(json.load(open("../upstream.lock.json"))["toolchain_commit"])')
if [ ! -x /workspace/tools/riscv32-gnu-toolchain/bin/riscv32-unknown-elf-gcc ] || \
   [ ! -x /workspace/tools/verilator/bin/verilator ] || \
   [ ! -x /workspace/tools/llvm-vortex/bin/clang ] || \
   [ ! -f /workspace/tools/libc32/lib/libc.a ] || \
   [ ! -f /workspace/tools/libcrt32/lib/baremetal/libclang_rt.builtins-riscv32.a ]; then
  TOOLCHAIN_REV="$tool_commit" ./ci/toolchain_install.sh --verilator --llvm --libcrt32 --libc32 --riscv32
fi
if [ ! -x /workspace/tools/yosys/bin/yosys ] || [ ! -x /workspace/tools/sv2v/bin/sv2v ]; then
  TOOLCHAIN_REV="$tool_commit" ./ci/toolchain_install.sh --sv2v --yosys --sta
fi
make -s -j4 -C "/workspace/vendor/$source_name/third_party"
make -s -j4 -C sw/kernel
make -s -j4 -C tests/regression/bar_slot_phase
make -s -j4 -C tests/regression/bar_generation
make -s -j4 -C sw/runtime/simx
make -s -j4 -C sw/runtime/rtlsim
make -s -j4 -C hw/unittest/barrier
