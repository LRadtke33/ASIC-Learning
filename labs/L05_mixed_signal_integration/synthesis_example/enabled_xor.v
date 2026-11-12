// Small, separate synthesis example for lesson 45. No reset is requested.
module enabled_xor (
    input wire clk,
    input wire en,
    input wire [1:0] a,
    input wire [1:0] b,
    output reg [1:0] q
);
    always @(posedge clk)
        if (en) q <= a ^ b;
endmodule
