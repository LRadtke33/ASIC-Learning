`timescale 1ns/1ps
// A level synchronizer, not an event-capture or multi-bit-transfer primitive.
module sync_bit (
    input  wire clk,
    input  wire reset_n,
    input  wire async_level,
    output wire synced_level
);
    (* ASYNC_REG = "TRUE" *) reg meta;
    (* ASYNC_REG = "TRUE" *) reg sync;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            meta <= 1'b0;
            sync <= 1'b0;
        end else begin
            meta <= async_level;
            sync <= meta;
        end
    end
    assign synced_level = sync;
endmodule
