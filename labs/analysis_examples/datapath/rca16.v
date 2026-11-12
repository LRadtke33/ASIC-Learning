module rca16(input [15:0] a, b, input cin, output [15:0] s, output cout);
  wire [16:0] c;
  assign c[0] = cin;
  assign cout = c[16];
  genvar i;
  generate
    for (i = 0; i < 16; i = i + 1) begin : g
      sky130_fd_sc_hd__fa_1 fa (
        .A(a[i]), .B(b[i]), .CIN(c[i]), .SUM(s[i]), .COUT(c[i+1])
      );
    end
  endgenerate
endmodule
