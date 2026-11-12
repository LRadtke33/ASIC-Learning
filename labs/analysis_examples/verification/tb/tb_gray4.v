`timescale 1ns/1ps
// Self-checking testbench for gray4.
// Stimulus and sampling both sit on the falling edge so they cannot race
// the DUT's rising-edge flops.  A `$display("FAIL")` plus an error
// counter is the whole scoreboard; the run exits non-zero on any miss.
module tb_gray4;
    reg clk = 0, rst_n = 0, en = 0;
    wire [3:0] gray, bin;
    integer errors, i;
    reg [3:0] prev, expected_bin;

    gray4 dut(.clk(clk), .rst_n(rst_n), .en(en), .gray(gray), .bin(bin));
    always #5 clk = ~clk; // 10 ns teaching period

    task require(input ok, input [8*64-1:0] msg);
        if (!ok) begin
            $display("FAIL at %0t: %0s  gray=%b bin=%0d", $time, msg, gray, bin);
            errors = errors + 1;
        end
    endtask

    function integer ham(input [3:0] a, input [3:0] b);
        integer k;
        begin
            ham = 0;
            for (k = 0; k < 4; k = k + 1) ham = ham + (a[k] ^ b[k]);
        end
    endfunction

    initial begin
        errors = 0;
        expected_bin = 0;
        $dumpfile("tb_gray4.vcd");
        $dumpvars(0, tb_gray4);
        // Hold reset through two falling edges, then release.
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        require(gray === 4'b0000, "reset value");
        require(bin  === 4'd0,    "reset bin");
        en = 1;
        prev = gray;
        for (i = 0; i < 32; i = i + 1) begin
            @(negedge clk);
            expected_bin = (expected_bin + 1) & 4'hF;
            require(bin === expected_bin, "bin sequence");
            require(ham(prev, gray) === 1, "Gray Hamming distance");
            require(gray === (bin ^ (bin >> 1)), "Gray encoding of bin");
            prev = gray;
        end
        en = 0;
        prev = gray;
        repeat (8) begin
            @(negedge clk);
            require(gray === prev, "stable when en=0");
        end
        if (errors == 0) $display("PASS  tb_gray4  32 steps + 8 holds, 0 errors");
        else             $display("FAIL  tb_gray4  %0d errors", errors);
        $finish;
    end
endmodule
