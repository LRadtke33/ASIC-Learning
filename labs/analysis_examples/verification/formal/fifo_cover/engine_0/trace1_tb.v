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
  reg [0:0] PI_rd;
  reg [7:0] PI_din;
  reg [0:0] PI_rst_n;
  wire [0:0] PI_clk = clock;
  reg [0:0] PI_wr;
  sync_fifo UUT (
    .rd(PI_rd),
    .din(PI_din),
    .rst_n(PI_rst_n),
    .clk(PI_clk),
    .wr(PI_wr)
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
    // UUT.$auto$async2sync.\cc:116:execute$430  = 1'b1;
    // UUT.$auto$async2sync.\cc:116:execute$436  = 1'b1;
    // UUT.$auto$async2sync.\cc:116:execute$442  = 1'b1;
    // UUT.$auto$async2sync.\cc:234:execute$374  = 1'b0;
    // UUT.$auto$async2sync.\cc:234:execute$376  = 1'b0;
    UUT._witness_.anyinit_procdff_267 = 1'b1;
    UUT._witness_.anyinit_procdff_268 = 1'b0;
    UUT._witness_.anyinit_procdff_269 = 3'b000;
    UUT._witness_.anyinit_procdff_310 = 8'b00000000;
    UUT._witness_.anyinit_procdff_315 = 2'b00;
    UUT._witness_.anyinit_procdff_320 = 2'b00;
    UUT._witness_.anyinit_procdff_325 = 3'b100;
    UUT.f_past_valid = 1'b0;
    UUT.\mem[0]  = 8'b00100000;
    UUT.\mem[1]  = 8'b00001000;
    UUT.\mem[2]  = 8'b00100000;
    UUT.\mem[3]  = 8'b00000000;

    // state 0
    PI_rd = 1'b0;
    PI_din = 8'b00000000;
    PI_rst_n = 1'b0;
    PI_wr = 1'b0;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00000001;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b1;
    end

    // state 2
    if (cycle == 1) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00001000;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b1;
    end

    // state 3
    if (cycle == 2) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00000000;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b1;
    end

    // state 4
    if (cycle == 3) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00000000;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b1;
    end

    // state 5
    if (cycle == 4) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00000001;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b0;
    end

    // state 6
    if (cycle == 5) begin
      PI_rd <= 1'b0;
      PI_din <= 8'b00000000;
      PI_rst_n <= 1'b1;
      PI_wr <= 1'b1;
    end

    genclock <= cycle < 6;
    cycle <= cycle + 1;
  end
endmodule
