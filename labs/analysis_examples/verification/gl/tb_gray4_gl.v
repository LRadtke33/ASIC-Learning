`timescale 1ns/1ps
`define FUNCTIONAL
`ifndef UNIT_DELAY
`define UNIT_DELAY #0.001
`endif
// PDK includes are supplied on the iverilog command line via -I and a wrapper.

module tb_gray4_gl;
    parameter USE_SDF = 0;
    reg clk = 0, rst_n = 0, en = 0;
    wire [3:0] gray, bin;
    integer errors, i;
    reg [3:0] prev, expected_bin;
    real t_clk, t_q, ckq_ns;
    integer ckq_n;
    real ckq_sum, ckq_min, ckq_max;

    gray4 dut(.clk(clk), .rst_n(rst_n), .en(en), .gray(gray), .bin(bin));
    always #5 clk = ~clk;

    initial begin
        if (USE_SDF) begin
            $sdf_annotate("gray4.sdf", dut, , "sdf_annotate.log", "TYPICAL");
            $display("SDF annotated (TYPICAL) onto dut");
        end else
            $display("GL simulation without SDF (unit-delay models only)");
    end

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

    // Measure CLK rising -> gray change (first bit that moves).
    always @(posedge clk) t_clk = $realtime;
    always @(gray) begin
        if (rst_n && en) begin
            t_q = $realtime;
            ckq_ns = t_q - t_clk;
            if (ckq_ns > 0.0 && ckq_ns < 5.0) begin
                ckq_sum = ckq_sum + ckq_ns;
                ckq_n = ckq_n + 1;
                if (ckq_ns < ckq_min) ckq_min = ckq_ns;
                if (ckq_ns > ckq_max) ckq_max = ckq_ns;
            end
        end
    end

    initial begin
        errors = 0; expected_bin = 0;
        ckq_n = 0; ckq_sum = 0; ckq_min = 1e9; ckq_max = 0;
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        require(gray === 4'b0000, "reset value");
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
        if (errors == 0) $display("PASS  tb_gray4_gl  USE_SDF=%0d  32 steps, 0 errors", USE_SDF);
        else             $display("FAIL  tb_gray4_gl  USE_SDF=%0d  %0d errors", USE_SDF, errors);
        if (ckq_n > 0)
            $display("CLK->Q  n=%0d  min=%.4f ns  mean=%.4f ns  max=%.4f ns",
                     ckq_n, ckq_min, ckq_sum/ckq_n, ckq_max);
        else
            $display("CLK->Q  no transitions captured");
        $finish;
    end
endmodule
