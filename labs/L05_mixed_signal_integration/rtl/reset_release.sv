`timescale 1ns/1ps
// Two-stage asynchronous assertion / synchronous release for one clock domain.
// Attributes express intent; the ASIC flow must preserve and place this chain.
module reset_release (
    input  wire clk,
    input  wire arst_n,
    output wire reset_n
);
    (* ASYNC_REG = "TRUE" *) reg [1:0] release_pipe;
    always @(posedge clk or negedge arst_n) begin
        if (!arst_n) release_pipe <= 2'b00;
        else         release_pipe <= {release_pipe[0], 1'b1};
    end
    assign reset_n = release_pipe[1];
endmodule
