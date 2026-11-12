`timescale 1ns/1ps
// CLK->Q measurement using specify delays copied from the OpenSTA 2.7 SDF
// for sky130_fd_sc_hd__dfrtp_1 instance _21_ in gray4.sdf:
//   (IOPATH CLK Q (0.374::0.374) (0.389::0.389))
// Icarus Verilog 12.0's $sdf_annotate did not apply those IOPATHs (confirmed
// on a one-buffer test); compiled specify delays do, and we measure them here.
module dfrtp_sdf (output Q, input CLK, D, RESET_B);
    reg qi;
    assign Q = qi;
    always @(posedge CLK or negedge RESET_B) begin
        if (!RESET_B) qi <= 1'b0;
        else          qi <= D;
    end
    specify
        (posedge CLK => (Q : CLK)) = (0.374, 0.389);
        (negedge RESET_B => (Q +: RESET_B)) = (0, 0);
    endspecify
endmodule

module tb_ckq_specify;
    reg clk = 0, rst_n = 0, d = 0;
    wire q;
    real tclk, tq, ckq, ckq_min, ckq_max, ckq_sum;
    integer n, rises, falls;
    dfrtp_sdf dut(.Q(q), .CLK(clk), .D(d), .RESET_B(rst_n));
    always #5 clk = ~clk;
    always @(posedge clk) tclk = $realtime;
    always @(q) begin
        if (rst_n) begin
            tq = $realtime;
            ckq = tq - tclk;
            if (ckq > 0 && ckq < 5) begin
                n = n + 1;
                ckq_sum = ckq_sum + ckq;
                if (ckq < ckq_min) ckq_min = ckq;
                if (ckq > ckq_max) ckq_max = ckq;
                if (q === 1'b1) rises = rises + 1;
                if (q === 1'b0) falls = falls + 1;
                $display("Q=%b  CLK->Q = %.4f ns", q, ckq);
            end
        end
    end
    initial begin
        n = 0; rises = 0; falls = 0; ckq_sum = 0; ckq_min = 1e9; ckq_max = 0;
        repeat (2) @(negedge clk);
        rst_n = 1;
        repeat (8) begin
            @(negedge clk);
            d = ~d;
        end
        @(negedge clk);
        $display("CKQ  n=%0d  rises=%0d  falls=%0d  min=%.4f  mean=%.4f  max=%.4f ns",
                 n, rises, falls, ckq_min, ckq_sum/n, ckq_max);
        $display("PASS  tb_ckq_specify  OpenSTA SDF IOPATH compiled as specify");
        $finish;
    end
endmodule
