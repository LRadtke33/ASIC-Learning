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
  reg [0:0] PI_rst_n;
  wire [0:0] PI_clk = clock;
  reg [0:0] PI_en;
  gray4 UUT (
    .rst_n(PI_rst_n),
    .clk(PI_clk),
    .en(PI_en)
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
    // UUT.$auto$async2sync.\cc:116:execute$161  = 1'b1;
    // UUT.$auto$async2sync.\cc:234:execute$129  = 1'b0;
    // UUT.$auto$async2sync.\cc:234:execute$131  = 1'b0;
    UUT._witness_.anyinit_procdff_119 = 4'b0000;
    UUT.f_past_valid = 1'b0;

    // state 0
    PI_rst_n = 1'b0;
    PI_en = 1'b1;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 2
    if (cycle == 1) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 3
    if (cycle == 2) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 4
    if (cycle == 3) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 5
    if (cycle == 4) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 6
    if (cycle == 5) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 7
    if (cycle == 6) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 8
    if (cycle == 7) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 9
    if (cycle == 8) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 10
    if (cycle == 9) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 11
    if (cycle == 10) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 12
    if (cycle == 11) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 13
    if (cycle == 12) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 14
    if (cycle == 13) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 15
    if (cycle == 14) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 16
    if (cycle == 15) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    // state 17
    if (cycle == 16) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b0;
    end

    // state 18
    if (cycle == 17) begin
      PI_rst_n <= 1'b1;
      PI_en <= 1'b1;
    end

    genclock <= cycle < 18;
    cycle <= cycle + 1;
  end
endmodule
