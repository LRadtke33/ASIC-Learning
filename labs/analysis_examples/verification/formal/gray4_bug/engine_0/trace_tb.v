`ifndef VERILATOR
module testbench;
  reg [4095:0] vcdfile;
  reg clock;
`else
module testbench(input clock, output reg genclock);
  initial genclock = 1;
`endif
  reg genclock = 1;
  reg [31:0] cycle = 0;
  reg [0:0] PI_en;
  wire [0:0] PI_clk = clock;
  reg [0:0] PI_rst_n;
  gray4 UUT (
    .en(PI_en),
    .clk(PI_clk),
    .rst_n(PI_rst_n)
  );
`ifndef VERILATOR
  initial begin
    if ($value$plusargs("vcd=%s", vcdfile)) begin
      $dumpfile(vcdfile);
      $dumpvars(0, testbench);
    end
    #5 clock = 0;
    while (genclock) begin
      #5 clock = 0;
      #5 clock = 1;
    end
  end
`endif
  initial begin
`ifndef VERILATOR
    #1;
`endif
    // UUT.$auto$async2sync.\cc:107:execute$64  = 1'b0;
    // UUT.$auto$async2sync.\cc:116:execute$68  = 1'b1;
    UUT._witness_.anyinit_procdff_45 = 1'b1;
    UUT._witness_.anyinit_procdff_46 = 1'b1;
    UUT._witness_.anyinit_procdff_47 = 4'b1100;
    UUT._witness_.anyinit_procdff_53 = 4'b0010;
    UUT.f_past_valid = 1'b0;

    // state 0
    PI_en = 1'b0;
    PI_rst_n = 1'b0;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_en <= 1'b1;
      PI_rst_n <= 1'b1;
    end

    // state 2
    if (cycle == 1) begin
      PI_en <= 1'b1;
      PI_rst_n <= 1'b1;
    end

    // state 3
    if (cycle == 2) begin
      PI_en <= 1'b0;
      PI_rst_n <= 1'b1;
    end

    // state 4
    if (cycle == 3) begin
      PI_en <= 1'b1;
      PI_rst_n <= 1'b1;
    end

    genclock <= cycle < 4;
    cycle <= cycle + 1;
  end
endmodule
