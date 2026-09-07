`include "VX_define.vh"

module VX_barrier_top import VX_gpu_pkg::*; (
    input wire clk,
    input wire reset,
    input wire req_valid,
    input wire [NW_WIDTH-1:0] req_wid,
    input wire is_arrive,
    input wire is_sync,
    input wire phase,
    input wire [BAR_SIZE_W-1:0] size_m1,
    input wire [BAR_ADDR_W-1:0] read_addr,
    output wire read_phase,
    output wire unlock_valid,
    output wire [`VX_CFG_NUM_WARPS-1:0] unlock_mask
);
    barrier_t request;
    assign request = '{id: '0, is_event: 1'b0, is_global: 1'b0,
                       is_arrive: is_arrive, is_sync: is_sync,
                       phase: phase, size_m1: size_m1};
    VX_gbar_bus_if gbar_bus_if();
    assign gbar_bus_if.req_ready = 1'b1;
    assign gbar_bus_if.rsp_valid = 1'b0;
    assign gbar_bus_if.rsp_data = '0;
    `UNUSED_VAR ({gbar_bus_if.req_valid, gbar_bus_if.req_data, gbar_bus_if.rsp_ready})

    VX_bar_unit #(.INSTANCE_ID("barrier"), .CORE_ID(0)) dut (
        .clk(clk), .reset(reset), .req_valid(req_valid), .req_wid(req_wid),
        .req_data(request), .read_addr(read_addr), .read_phase(read_phase),
        .gbar_bus_if(gbar_bus_if), .active_warps({`VX_CFG_NUM_WARPS{1'b1}}),
        .unlock_valid(unlock_valid), .unlock_mask(unlock_mask)
    );
endmodule
