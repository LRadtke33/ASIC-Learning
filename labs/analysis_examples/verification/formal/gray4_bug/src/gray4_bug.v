`timescale 1ns/1ps
// Deliberately wrong "Gray" counter: it is a plain binary counter.
// Formal BMC of the Hamming-distance-1 property is expected to FAIL.
module gray4 (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    output reg  [3:0] gray,
    output wire [3:0] bin
);
    assign bin = gray; // pretends the output is already "bin"
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) gray <= 4'b0000;
        else if (en) gray <= gray + 4'd1;
    end
`ifdef FORMAL
    initial assume (rst_n == 1'b0);
    reg f_past_valid = 1'b0;
    always @(posedge clk) f_past_valid <= 1'b1;
    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && $past(en))
            assert ($countones(gray ^ $past(gray)) == 4'd1);
    end
`endif
endmodule
