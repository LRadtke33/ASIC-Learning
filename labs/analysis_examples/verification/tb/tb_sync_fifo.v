`timescale 1ns/1ps
// Self-checking testbench for sync_fifo, with a queue scoreboard.
// Drive and sample on the falling edge (see tb_gray4.v).
module tb_sync_fifo;
    reg clk = 0, rst_n = 0, wr = 0, rd = 0;
    reg [7:0] din = 0;
    wire [7:0] dout;
    wire full, empty;
    wire [2:0] count;
    integer errors, i;
    // Scoreboard queue: expected output stream, in write order.
    reg [7:0] sb [0:15];
    integer sb_h, sb_t;

    sync_fifo dut(.clk(clk), .rst_n(rst_n), .wr(wr), .rd(rd),
                  .din(din), .dout(dout), .full(full), .empty(empty), .count(count));
    always #5 clk = ~clk;

    task require(input ok, input [8*64-1:0] msg);
        if (!ok) begin
            $display("FAIL at %0t: %0s  full=%b empty=%b count=%0d dout=%0h",
                     $time, msg, full, empty, count, dout);
            errors = errors + 1;
        end
    endtask

    task push(input [7:0] d);
        begin
            @(negedge clk);
            din = d; wr = 1; rd = 0;
            sb[sb_t] = d; sb_t = sb_t + 1;
            @(negedge clk);
            wr = 0;
        end
    endtask

    // Registered-read FIFO: assert rd through one rising edge, then sample dout.
    task pop_expect;
        begin
            @(negedge clk);
            wr = 0; rd = 1;
            @(negedge clk);
            rd = 0;
            require(dout === sb[sb_h], "scoreboard pop order");
            sb_h = sb_h + 1;
        end
    endtask

    initial begin
        errors = 0; sb_h = 0; sb_t = 0;
        $dumpfile("tb_sync_fifo.vcd");
        $dumpvars(0, tb_sync_fifo);
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        require(empty === 1 && full === 0 && count === 0, "reset empty");

        push(8'hA0); push(8'hA1); push(8'hA2); push(8'hA3);
        @(negedge clk);
        require(full === 1 && empty === 0 && count === 3'd4, "full after 4 writes");

        // A write while full must be ignored (count and occupancy stay 4).
        @(negedge clk);
        din = 8'hFF; wr = 1;
        @(negedge clk);
        wr = 0;
        require(full === 1 && count === 3'd4, "write-to-full ignored");

        pop_expect; pop_expect; pop_expect; pop_expect;
        @(negedge clk);
        require(empty === 1 && full === 0 && count === 0, "empty after 4 reads");

        // Simultaneous wr+rd on a mid-fill: occupancy stays, data still flows.
        push(8'h11);
        push(8'h22);
        @(negedge clk);
        din = 8'h33; wr = 1; rd = 1;
        sb[sb_t] = 8'h33; sb_t = sb_t + 1;
        @(negedge clk);
        wr = 0; rd = 0;
        require(count === 3'd2, "count after simultaneous wr/rd on 2-deep");
        // The just-completed rd presented the first pushed mid-fill byte (0x11).
        require(dout === 8'h11, "simultaneous-cycle presented 0x11");
        sb_h = sb_h + 1; // 0x11 already consumed on the simultaneous cycle
        pop_expect; // should be 0x22
        pop_expect; // should be 0x33
        @(negedge clk);
        require(empty === 1, "empty at end");

        if (errors == 0) $display("PASS  tb_sync_fifo  fill/full-ignore/drain/simultaneous, 0 errors");
        else             $display("FAIL  tb_sync_fifo  %0d errors", errors);
        $finish;
    end
endmodule
