// 4-deep, 8-bit synchronous FIFO. Teaching netlist for lesson 36.
// Incremental write and read pointers; full/empty from a wrap count.
`timescale 1ns/1ps
module sync_fifo (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       wr,
    input  wire       rd,
    input  wire [7:0] din,
    output reg  [7:0] dout,
    output wire       full,
    output wire       empty,
    output wire [2:0] count
);
    reg [7:0] mem [0:3];
    reg [1:0] wptr, rptr;
    reg [2:0] cnt;
    assign count = cnt;
    assign full  = (cnt == 3'd4);
    assign empty = (cnt == 3'd0);
    wire do_wr = wr && !full;
    wire do_rd = rd && !empty;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wptr <= 2'd0;
            rptr <= 2'd0;
            cnt  <= 3'd0;
            dout <= 8'd0;
        end else begin
            if (do_wr) begin
                mem[wptr] <= din;
                wptr <= wptr + 2'd1;
            end
            if (do_rd) begin
                dout <= mem[rptr];
                rptr <= rptr + 2'd1;
            end
            case ({do_wr, do_rd})
                2'b10: cnt <= cnt + 3'd1;
                2'b01: cnt <= cnt - 3'd1;
                default: cnt <= cnt;
            endcase
        end
    end
endmodule
