// 4-bit Gray-code counter. Teaching netlist for lesson 36.
// After reset, gray is 0000. While en is high, each clock advances
// one Gray step (Hamming distance 1), wrapping 1000 -> 0000.
`timescale 1ns/1ps
module gray4 (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    output reg  [3:0] gray,
    output wire [3:0] bin
);
    // Standard binary-to-Gray of (bin+1)
    assign bin = {gray[3], gray[3]^gray[2], gray[3]^gray[2]^gray[1],
                  gray[3]^gray[2]^gray[1]^gray[0]};
    wire [3:0] bin_next = bin + 4'd1;
    wire [3:0] gray_next = bin_next ^ (bin_next >> 1);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) gray <= 4'b0000;
        else if (en) gray <= gray_next;
    end
endmodule
