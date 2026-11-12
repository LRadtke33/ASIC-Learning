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

`ifdef FORMAL
    initial assume (rst_n == 1'b0);

    reg f_past_valid = 1'b0;
    always @(posedge clk) f_past_valid <= 1'b1;

    reg f_seen_reset = 1'b0;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) f_seen_reset <= 1'b1;
    end

    // Combinational consistency holds once a reset has taken effect.
    always @(*) begin
        if (f_seen_reset) begin
            assert (!(full && empty));
            assert (full  == (count == 3'd4));
            assert (empty == (count == 3'd0));
            assert (count <= 3'd4);
        end
    end

    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n) begin
            if ($past(wr) && !$past(full) && !($past(rd) && !$past(empty)))
                assert (count == $past(count) + 3'd1);
            if ($past(rd) && !$past(empty) && !($past(wr) && !$past(full)))
                assert (count == $past(count) - 3'd1);
            if ($past(wr) && !$past(full) && $past(rd) && !$past(empty))
                assert (count == $past(count));
            if (!($past(wr) && !$past(full)) && !($past(rd) && !$past(empty)))
                assert (count == $past(count));
        end
    end

    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && $past(full) && $past(wr) && !$past(rd))
            assert (count == 3'd4 && full);
    end

    always @(posedge clk) begin
        if (!rst_n) assert (empty && !full && count == 3'd0);
    end

    always @(posedge clk) cover (f_seen_reset && full);
    reg f_seen_full = 1'b0;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) f_seen_full <= 1'b0;
        else if (full) f_seen_full <= 1'b1;
    end
    always @(posedge clk) cover (f_past_valid && f_seen_reset && f_seen_full && empty && rst_n);
    always @(posedge clk) cover (f_past_valid && f_seen_reset && rst_n && $past(wr) && $past(rd) && $past(count) == 3'd2);
`endif
endmodule
