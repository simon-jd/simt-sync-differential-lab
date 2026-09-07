module VX_dp_ram (
	clk,
	reset,
	read,
	write,
	wren,
	waddr,
	wdata,
	raddr,
	rdata
);
	parameter DATAW = 1;
	parameter SIZE = 1;
	parameter WRENW = 1;
	parameter OUT_REG = 0;
	parameter LUTRAM = 0;
	parameter RDW_MODE = "W";
	parameter RADDR_REG = 0;
	parameter RADDR_RESET = 0;
	parameter RDW_ASSERT = 0;
	parameter RESET_RAM = 0;
	parameter INIT_ENABLE = 0;
	parameter INIT_FILE = "";
	parameter [DATAW - 1:0] INIT_VALUE = 0;
	parameter ADDRW = (SIZE > 1 ? $clog2(SIZE) : 1);
	input wire clk;
	input wire reset;
	input wire read;
	input wire write;
	input wire [WRENW - 1:0] wren;
	input wire [ADDRW - 1:0] waddr;
	input wire [DATAW - 1:0] wdata;
	input wire [ADDRW - 1:0] raddr;
	output wire [DATAW - 1:0] rdata;
	localparam WSELW = DATAW / WRENW;
	localparam FORCE_BRAM = !LUTRAM && ((SIZE >= 64) && ((SIZE * DATAW) >= 2048));
	localparam FORCE_BRAM_ASYNC = (FORCE_BRAM && (OUT_REG == 0)) && (RDW_MODE == "R");
	generate
		if (1) begin : g_no_asic
			if (OUT_REG != 0) begin : g_sync
				if (FORCE_BRAM) begin : g_bram
					if (RDW_MODE == "W") begin : g_write_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_1
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_2
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_3
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
					end
					else if (RDW_MODE == "R") begin : g_read_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_4
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_5
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_6
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
					end
				end
				else if (LUTRAM) begin : g_lutram
					if (RDW_MODE == "W") begin : g_write_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_7
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_8
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_9
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
					end
					else if (RDW_MODE == "R") begin : g_read_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_10
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_11
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_12
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
					end
				end
				else begin : g_auto
					if (RDW_MODE == "W") begin : g_write_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_13
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_14
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_15
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [ADDRW - 1:0] raddr_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									raddr_r <= raddr;
							end
							assign rdata = ram[raddr_r];
						end
					end
					else if (RDW_MODE == "R") begin : g_read_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_16
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write) begin : sv2v_autoblock_17
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_18
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							reg [DATAW - 1:0] rdata_r;
							always @(posedge clk) begin
								if (write)
									ram[waddr] <= wdata;
								if (read)
									rdata_r <= ram[raddr];
							end
							assign rdata = rdata_r;
						end
					end
				end
			end
			else begin : g_async
				if (FORCE_BRAM_ASYNC) begin : g_bram
					if (RDW_MODE == "W") begin : g_write_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_19
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write) begin : sv2v_autoblock_20
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
							assign rdata = ram[raddr];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_21
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write)
									ram[waddr] <= wdata;
							assign rdata = ram[raddr];
						end
					end
					else begin : g_read_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_22
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write) begin : sv2v_autoblock_23
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
							assign rdata = ram[raddr];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_24
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write)
									ram[waddr] <= wdata;
							assign rdata = ram[raddr];
						end
					end
				end
				else begin : g_auto
					if (RDW_MODE == "W") begin : g_write_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_25
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write) begin : sv2v_autoblock_26
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
							assign rdata = ram[raddr];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_27
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write)
									ram[waddr] <= wdata;
							assign rdata = ram[raddr];
						end
					end
					else begin : g_read_first
						if (WRENW != 1) begin : g_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_28
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write) begin : sv2v_autoblock_29
									integer i;
									for (i = 0; i < WRENW; i = i + 1)
										if (wren[i])
											ram[waddr][i * WSELW+:WSELW] <= wdata[i * WSELW+:WSELW];
								end
							assign rdata = ram[raddr];
						end
						else begin : g_no_wren
							reg [DATAW - 1:0] ram [0:SIZE - 1];
							if (INIT_ENABLE != 0) begin : g_init
								if (INIT_FILE != "") begin : g_file
									initial $readmemh(INIT_FILE, ram);
								end
								else begin : g_value
									initial begin : sv2v_autoblock_30
										integer i;
										for (i = 0; i < SIZE; i = i + 1)
											begin : g_i
												ram[i] = INIT_VALUE;
											end
									end
								end
							end
							always @(posedge clk)
								if (write)
									ram[waddr] <= wdata;
							assign rdata = ram[raddr];
						end
					end
				end
			end
		end
	endgenerate
endmodule
module VX_barrier_top (
	clk,
	reset,
	req_valid,
	req_wid,
	is_arrive,
	is_sync,
	phase,
	size_m1,
	read_addr,
	read_phase,
	unlock_valid,
	unlock_mask
);
	input wire clk;
	input wire reset;
	input wire req_valid;
	localparam VX_gpu_pkg_NW_BITS = 2;
	localparam VX_gpu_pkg_NW_WIDTH = VX_gpu_pkg_NW_BITS;
	input wire [1:0] req_wid;
	input wire is_arrive;
	input wire is_sync;
	input wire phase;
	localparam VX_gpu_pkg_NC_BITS = 0;
	localparam VX_gpu_pkg_NC_WIDTH = 1;
	localparam VX_gpu_pkg_BAR_SIZE_W = 5;
	input wire [4:0] size_m1;
	localparam VX_gpu_pkg_NB_BITS = 3;
	localparam VX_gpu_pkg_BAR_ADDR_BITS = 5;
	localparam VX_gpu_pkg_BAR_ADDR_W = VX_gpu_pkg_BAR_ADDR_BITS;
	input wire [4:0] read_addr;
	output wire read_phase;
	output wire unlock_valid;
	output wire [3:0] unlock_mask;
	localparam VX_gpu_pkg_NB_WIDTH = VX_gpu_pkg_NB_BITS;
	wire [12:0] request;
	function automatic [2:0] sv2v_cast_94458;
		input reg [2:0] inp;
		sv2v_cast_94458 = inp;
	endfunction
	function automatic [4:0] sv2v_cast_1C6DC;
		input reg [4:0] inp;
		sv2v_cast_1C6DC = inp;
	endfunction
	assign request = {sv2v_cast_94458(1'sb0), 2'b00, is_arrive, is_sync, phase, sv2v_cast_1C6DC(size_m1)};
	generate
		if (1) begin : gbar_bus_if
			wire req_valid;
			localparam VX_gpu_pkg_NB_BITS = 3;
			localparam VX_gpu_pkg_NB_WIDTH = VX_gpu_pkg_NB_BITS;
			localparam VX_gpu_pkg_NC_BITS = 0;
			localparam VX_gpu_pkg_NC_WIDTH = 1;
			wire [4:0] req_data;
			wire req_ready;
			wire rsp_valid;
			wire [2:0] rsp_data;
			wire rsp_ready;
		end
	endgenerate
	assign gbar_bus_if.req_ready = 1'b1;
	assign gbar_bus_if.rsp_valid = 1'b0;
	assign gbar_bus_if.rsp_data = 1'sb0;
	localparam _param_08EFF_INSTANCE_ID = "barrier";
	localparam _param_08EFF_CORE_ID = 0;
	function automatic [5:0] sv2v_cast_6;
		input reg [5:0] inp;
		sv2v_cast_6 = inp;
	endfunction
	function automatic [1:0] sv2v_cast_2;
		input reg [1:0] inp;
		sv2v_cast_2 = inp;
	endfunction
	function automatic [0:0] sv2v_cast_1;
		input reg [0:0] inp;
		sv2v_cast_1 = inp;
	endfunction
	generate
		if (1) begin : dut
			localparam INSTANCE_ID = _param_08EFF_INSTANCE_ID;
			localparam CORE_ID = _param_08EFF_CORE_ID;
			wire clk;
			wire reset;
			wire req_valid;
			localparam VX_gpu_pkg_NW_BITS = 2;
			localparam VX_gpu_pkg_NW_WIDTH = VX_gpu_pkg_NW_BITS;
			wire [1:0] req_wid;
			localparam VX_gpu_pkg_NC_BITS = 0;
			localparam VX_gpu_pkg_NC_WIDTH = 1;
			localparam VX_gpu_pkg_BAR_SIZE_W = 5;
			localparam VX_gpu_pkg_NB_BITS = 3;
			localparam VX_gpu_pkg_NB_WIDTH = VX_gpu_pkg_NB_BITS;
			wire [12:0] req_data;
			localparam VX_gpu_pkg_BAR_ADDR_BITS = 5;
			localparam VX_gpu_pkg_BAR_ADDR_W = VX_gpu_pkg_BAR_ADDR_BITS;
			wire [4:0] read_addr;
			wire read_phase;
			wire [3:0] active_warps;
			wire unlock_valid;
			wire [3:0] unlock_mask;
			localparam EVENT_WIDTH = 6;
			localparam BAR_STATEW = 12;
			localparam USE_GBAR = 1'd0;
			wire [3:0] mask_r;
			reg [3:0] mask_n;
			wire [1:0] count_r;
			reg [1:0] count_n;
			wire [5:0] events_r;
			reg [5:0] events_n;
			reg phase_r;
			reg phase_n;
			reg unlock_valid_n;
			reg [3:0] unlock_mask_n;
			reg gbar_req_valid_r;
			reg gbar_req_valid_n;
			reg [2:0] gbar_req_id_r;
			reg [2:0] gbar_req_id_n;
			reg [0:0] gbar_req_size_m1_r;
			reg [0:0] gbar_req_size_m1_n;
			wire gbar_rsp_ready = ~req_valid;
			wire [3:0] wait_mask = (4'sd1 << req_wid) | mask_r;
			wire [1:0] next_count = count_r + 2'sd1;
			wire next_phase = ~phase_r;
			always @(*) begin
				mask_n = mask_r;
				count_n = count_r;
				events_n = events_r;
				phase_n = phase_r;
				unlock_valid_n = 0;
				unlock_mask_n = 1'sbx;
				gbar_req_valid_n = gbar_req_valid_r;
				gbar_req_id_n = gbar_req_id_r;
				gbar_req_size_m1_n = gbar_req_size_m1_r;
				if (req_valid && ~req_data[8]) begin
					if (req_data[9]) begin
						if (req_data[5])
							events_n = (events_r + sv2v_cast_6(req_data[4-:VX_gpu_pkg_BAR_SIZE_W])) + 6'sd1;
						else
							events_n = events_r - 6'sd1;
						if (((req_data[5] == 0) && (events_r == 6'sd1)) && (count_r == 0)) begin
							mask_n = 1'sb0;
							unlock_valid_n = 1;
							unlock_mask_n = mask_r;
							phase_n = next_phase;
						end
					end
					else if (req_data[7]) begin
						if (count_r == sv2v_cast_2(req_data[4-:VX_gpu_pkg_BAR_SIZE_W])) begin
							count_n = 1'sb0;
							if (events_r == 0) begin
								mask_n = 1'sb0;
								unlock_valid_n = 1;
								unlock_mask_n = (req_data[6] ? wait_mask : mask_r);
								phase_n = next_phase;
							end
							else if (req_data[6])
								mask_n = wait_mask;
						end
						else begin
							count_n = next_count;
							if (req_data[6])
								mask_n = wait_mask;
						end
					end
					else if (req_data[5] != phase_r) begin
						unlock_valid_n = 1;
						unlock_mask_n = 4'sd1 << req_wid;
					end
					else
						mask_n = wait_mask;
				end
				if (USE_GBAR) begin
					if (req_valid && req_data[8]) begin
						if (req_data[9]) begin
							if (req_data[5])
								events_n = (events_r + sv2v_cast_6(req_data[4-:VX_gpu_pkg_BAR_SIZE_W])) + 6'sd1;
							else
								events_n = events_r - 6'sd1;
							if (((req_data[5] == 0) && (events_r == 6'sd1)) && (wait_mask == active_warps)) begin
								mask_n = 1'sb0;
								gbar_req_valid_n = 1;
								gbar_req_id_n = req_data[12-:3];
								gbar_req_size_m1_n = sv2v_cast_1(count_r);
							end
						end
						else if (req_data[7]) begin
							count_n = sv2v_cast_2(req_data[4-:VX_gpu_pkg_BAR_SIZE_W]);
							if ((wait_mask == active_warps) && (events_r == 0)) begin
								mask_n = 1'sb0;
								gbar_req_valid_n = 1;
								gbar_req_id_n = req_data[12-:3];
								gbar_req_size_m1_n = sv2v_cast_1(req_data[4-:VX_gpu_pkg_BAR_SIZE_W]);
							end
							else
								mask_n = wait_mask;
						end
						else if (req_data[5] != phase_r) begin
							unlock_valid_n = 1;
							unlock_mask_n = 4'sd1 << req_wid;
						end
						else
							mask_n = wait_mask;
					end
					if ((VX_barrier_top.gbar_bus_if.rsp_valid && gbar_rsp_ready) && (VX_barrier_top.gbar_bus_if.rsp_data[2-:3] == gbar_req_id_r)) begin
						unlock_valid_n = 1;
						unlock_mask_n = active_warps;
						phase_n = next_phase;
					end
					if (gbar_req_valid_r && VX_barrier_top.gbar_bus_if.req_ready)
						gbar_req_valid_n = 0;
				end
			end
			wire [11:0] store_state_rdata;
			wire store_phase_rdata;
			wire [4:0] store_raddr = read_addr;
			reg [4:0] store_waddr;
			wire [11:0] store_state_wdata = {mask_n, count_n, events_n};
			wire store_phase_wdata = phase_n;
			wire store_write = req_valid || VX_barrier_top.gbar_bus_if.rsp_valid;
			VX_dp_ram #(
				.DATAW(BAR_STATEW),
				.SIZE(32),
				.RDW_MODE("W"),
				.OUT_REG(1)
			) barrier_state_store(
				.clk(clk),
				.reset(reset),
				.read(1'b1),
				.write(store_write),
				.wren(1'b1),
				.raddr(store_raddr),
				.waddr(store_waddr),
				.wdata(store_state_wdata),
				.rdata(store_state_rdata)
			);
			VX_dp_ram #(
				.DATAW(1),
				.SIZE(32),
				.RDW_MODE("W"),
				.RADDR_REG(1)
			) barrier_phase_store(
				.clk(clk),
				.reset(reset),
				.read(1'b1),
				.write(store_write),
				.wren(1'b1),
				.raddr(store_raddr),
				.waddr(store_waddr),
				.wdata(store_phase_wdata),
				.rdata(store_phase_rdata)
			);
			reg [31:0] store_valids;
			wire is_rdw_hazard = store_write && (store_waddr == store_raddr);
			wire store_phase_rdata_v = (store_valids[store_raddr] ? store_phase_rdata : 1'b0);
			always @(posedge clk) begin
				if (reset) begin
					store_valids <= 1'sb0;
					phase_r <= 1'sb0;
				end
				else begin
					if (store_write)
						store_valids[store_waddr] <= 1'b1;
					phase_r <= (is_rdw_hazard ? store_phase_wdata : store_phase_rdata_v);
				end
				store_waddr <= store_raddr;
			end
			assign {mask_r, count_r, events_r} = (store_valids[store_waddr] ? store_state_rdata : {12 {1'sb0}});
			wire phase_async = (is_rdw_hazard ? phase_n : store_phase_rdata_v);
			reg unlock_valid_r;
			reg [3:0] unlock_mask_r;
			always @(posedge clk) begin
				if (reset)
					unlock_valid_r <= 0;
				else
					unlock_valid_r <= unlock_valid_n;
				unlock_mask_r <= unlock_mask_n;
			end
			assign read_phase = phase_async;
			assign unlock_valid = unlock_valid_r;
			assign unlock_mask = unlock_mask_r;
			if (USE_GBAR) begin : g_gbar
				always @(posedge clk) begin
					if (reset)
						gbar_req_valid_r <= 0;
					else
						gbar_req_valid_r <= gbar_req_valid_n;
					gbar_req_size_m1_r <= gbar_req_size_m1_n;
					gbar_req_id_r <= gbar_req_id_n;
				end
				assign VX_barrier_top.gbar_bus_if.req_valid = gbar_req_valid_r;
				assign VX_barrier_top.gbar_bus_if.req_data[4-:3] = gbar_req_id_r;
				assign VX_barrier_top.gbar_bus_if.req_data[1-:1] = gbar_req_size_m1_r;
				assign VX_barrier_top.gbar_bus_if.req_data[0-:1] = 1'sd0;
				assign VX_barrier_top.gbar_bus_if.rsp_ready = gbar_rsp_ready;
			end
			else begin : g_nogbar
				wire [1:1] sv2v_tmp_9448A;
				assign sv2v_tmp_9448A = 0;
				always @(*) gbar_req_valid_r = sv2v_tmp_9448A;
				wire [1:1] sv2v_tmp_2C0AD;
				assign sv2v_tmp_2C0AD = 1'sbx;
				always @(*) gbar_req_size_m1_r = sv2v_tmp_2C0AD;
				wire [3:1] sv2v_tmp_8951D;
				assign sv2v_tmp_8951D = 1'sbx;
				always @(*) gbar_req_id_r = sv2v_tmp_8951D;
				assign VX_barrier_top.gbar_bus_if.req_valid = 0;
				assign VX_barrier_top.gbar_bus_if.req_data = 1'sbx;
				assign VX_barrier_top.gbar_bus_if.rsp_ready = 0;
			end
		end
	endgenerate
	assign dut.clk = clk;
	assign dut.reset = reset;
	assign dut.req_valid = req_valid;
	assign dut.req_wid = req_wid;
	assign dut.req_data = request;
	assign dut.read_addr = read_addr;
	assign read_phase = dut.read_phase;
	assign dut.active_warps = {4 {1'b1}};
	assign unlock_valid = dut.unlock_valid;
	assign unlock_mask = dut.unlock_mask;
endmodule
