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

`ifdef FORMAL
    // Formal starts in reset so initial register values cannot be arbitrary.
    initial assume (rst_n == 1'b0);

    reg f_past_valid = 1'b0;
    always @(posedge clk) f_past_valid <= 1'b1;

    always @(posedge clk) begin
        if (f_past_valid && !$past(rst_n))
            assert (gray == 4'b0000);
    end

    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && $past(en))
            assert ($countones(gray ^ $past(gray)) == 4'd1);
    end

    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && !$past(en))
            assert (gray == $past(gray));
    end

    always @(*) begin
        assert (gray == (bin ^ (bin >> 1)));
    end

    // Cover a full wrap after a real reset: 0000 .. 1000 .. 0000.
    reg f_seen_reset = 1'b0;
    reg f_seen_1000  = 1'b0;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            f_seen_reset <= 1'b1;
            f_seen_1000  <= 1'b0;
        end else if (f_seen_reset && gray == 4'b1000) begin
            f_seen_1000 <= 1'b1;
        end
    end
    always @(posedge clk) begin
        cover (f_past_valid && f_seen_reset && f_seen_1000 && gray == 4'b0000 && rst_n);
    end
`endif
endmodule
