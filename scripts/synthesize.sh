#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/synthesis
rtl=vendor/vortex/hw/rtl
tools/sv2v/bin/sv2v --top=VX_barrier_top -DSYNTHESIS -DVX_CFG_XLEN=32 -DVX_CFG_XLEN_32 \
  -Ibuild32/hw -I"$rtl" -I"$rtl/libs" -Ivendor/vortex/hw/dpi \
  "$rtl/VX_gpu_pkg.sv" "$rtl/mem/VX_gbar_bus_if.sv" \
  "$rtl/libs/VX_dp_ram.sv" "$rtl/core/VX_bar_unit.sv" \
  overlays/hw/unittest/barrier/VX_barrier_top.sv \
  > artifacts/synthesis/barrier.v
tools/yosys/bin/yosys -p '
  read_verilog artifacts/synthesis/barrier.v;
  hierarchy -check -top VX_barrier_top;
  synth -top VX_barrier_top;
  check -assert;
  stat;
' > artifacts/synthesis/yosys.log
sha256sum artifacts/synthesis/barrier.v > artifacts/synthesis/barrier.sha256
