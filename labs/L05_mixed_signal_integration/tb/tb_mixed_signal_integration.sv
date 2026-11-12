`timescale 1ns/1ps
module tb_mixed_signal_integration;
    localparam integer WIDTH = 16;
    localparam integer MAX_WORDS = 512;
    reg src_clk = 1'b0, dst_clk = 1'b0;
    reg dst_running = 1'b1;
    reg por_n = 1'b0, analog_power_good = 1'b0, analog_ready = 1'b0;
    reg src_send = 1'b0;
    reg [WIDTH-1:0] src_word = '0;
    wire src_ready, src_busy, src_accept, src_reject, dst_valid;
    wire src_reset_n, dst_reset_n;
    wire [WIDTH-1:0] dst_word;
    integer src_half_ns = 7, dst_half_ns = 11, dst_phase_ns = 3;
    integer seed = 4369;
    reg [15:0] prng;
    integer qhead = 0, qtail = 0;
    integer accepted_total = 0, delivered_total = 0, aborted_total = 0;
    integer rejected_total = 0, epoch = 0;
    reg [WIDTH-1:0] expected [0:MAX_WORDS-1];
    realtime accepted_at [0:MAX_WORDS-1];
    integer accepted_epoch [0:MAX_WORDS-1];
    realtime last_src_edge = -1, last_dst_edge = -1;
    realtime min_latency = 1.0e9, max_latency = 0;
    integer trace_fd;

    mixed_signal_mailbox #(.WIDTH(WIDTH)) dut(.*);

    task automatic require(input logic ok, input string message);
        if (ok !== 1'b1) $fatal(1, "FAIL at %0.3f ns: %s", $realtime, message);
    endtask
    function automatic [15:0] next_prng(input [15:0] x);
        next_prng = {x[14:0], x[15] ^ x[13] ^ x[12] ^ x[10]};
    endfunction

    initial begin
        if ($value$plusargs("SRC_HALF_NS=%d", src_half_ns)) begin end
        if ($value$plusargs("DST_HALF_NS=%d", dst_half_ns)) begin end
        if ($value$plusargs("DST_PHASE_NS=%d", dst_phase_ns)) begin end
        if ($value$plusargs("SEED=%d", seed)) begin end
        require(src_half_ns > 0 && dst_half_ns > 0 && dst_phase_ns >= 0,
                "clock parameters must be positive, with nonnegative phase");
        prng = seed[15:0];
        if (prng == 0) prng = 16'h0001;
        trace_fd = $fopen("trace.csv", "w");
        require(trace_fd != 0, "cannot open trace.csv");
        $fdisplay(trace_fd, "event,epoch,time_ns,word_hex,latency_ns");
        $display("CONFIG source_period=%0d ns readout_period=%0d ns readout_phase=%0d ns seed=%0d",
                 2*src_half_ns, 2*dst_half_ns, dst_phase_ns, seed);
        if ($test$plusargs("WAVES")) begin
            $dumpfile("wave.vcd");
            $dumpvars(0, tb_mixed_signal_integration);
        end
        fork
            forever begin #(src_half_ns); src_clk = ~src_clk; end
            begin
                #(dst_phase_ns);
                forever begin
                    #(dst_half_ns);
                    if (dst_running) dst_clk = ~dst_clk;
                    else dst_clk = 1'b0;
                end
            end
        join
    end

    // Monitor after nonblocking assignments. Sample the offer before the edge.
    reg offered, ready_before, reset_before;
    reg [WIDTH-1:0] word_before;
    always @(posedge src_clk) begin
        last_src_edge = $realtime;
        offered = src_send;
        ready_before = src_ready;
        reset_before = src_reset_n;
        word_before = src_word;
        #0.001;
        if (dut.link_arst_n && reset_before) begin
            require(src_accept === (offered && ready_before), "source acceptance contract");
            require(src_reject === (offered && !ready_before), "busy rejection contract");
            if (src_reject) rejected_total = rejected_total + 1;
            if (src_accept) begin
                require(qtail < MAX_WORDS, "scoreboard capacity exceeded");
                expected[qtail] = word_before;
                accepted_at[qtail] = $realtime;
                accepted_epoch[qtail] = epoch;
                qtail = qtail + 1;
                accepted_total = accepted_total + 1;
                $fdisplay(trace_fd, "accept,%0d,%0.3f,%04h,", epoch, $realtime, word_before);
            end
        end
    end

    realtime latency;
    always @(posedge dst_clk) begin
        last_dst_edge = $realtime;
        #0.001;
        if (dut.link_arst_n && dst_reset_n && dst_valid) begin
            require(qhead < qtail, "duplicate, stale, or unsolicited destination word");
            require(dst_word === expected[qhead], "corrupted or out-of-order word");
            require(accepted_epoch[qhead] == epoch, "word crossed a reset epoch");
            latency = $realtime - accepted_at[qhead];
            if (latency < min_latency) min_latency = latency;
            if (latency > max_latency) max_latency = latency;
            $fdisplay(trace_fd, "deliver,%0d,%0.3f,%04h,%0.3f", epoch, $realtime, dst_word, latency);
            qhead = qhead + 1;
            delivered_total = delivered_total + 1;
        end
    end

    // Reset/invalidity cancels only accepted words not yet delivered.
    integer k;
    always @(negedge dut.link_arst_n) begin
        if ($realtime > 0) begin
            for (k=qhead; k<qtail; k=k+1)
                $fdisplay(trace_fd, "abort,%0d,%0.3f,%04h,", epoch, $realtime, expected[k]);
            aborted_total = aborted_total + (qtail - qhead);
            qhead = qtail;
            epoch = epoch + 1;
        end
        #0.001;
        require(src_reset_n === 1'b0 && dst_reset_n === 1'b0,
                "reset must assert even if readout clock is stopped");
        require(src_ready === 1'b0 && dst_valid === 1'b0,
                "interface must be invalid during reset");
    end
    always @(posedge src_reset_n)
        require($realtime == last_src_edge, "source reset release must align to source clock");
    always @(posedge dst_reset_n)
        require($realtime == last_dst_edge, "readout reset release must align to readout clock");

    // The held data must not change within a busy interval.
    reg previously_busy = 1'b0;
    reg [WIDTH-1:0] held_previous;
    always @(negedge src_clk) begin
        if (!src_reset_n) previously_busy = 1'b0;
        else begin
            if (previously_busy && src_busy)
                require(dut.mailbox_word === held_previous, "mailbox changed while busy");
            previously_busy = src_busy;
            held_previous = dut.mailbox_word;
        end
    end

    task automatic offer(input [WIDTH-1:0] word);
        @(negedge src_clk);
        src_word = word;
        src_send = 1'b1;
        @(negedge src_clk);
        src_send = 1'b0;
    endtask
    task automatic send_when_ready(input [WIDTH-1:0] word);
        @(negedge src_clk);
        while (src_ready !== 1'b1) @(negedge src_clk);
        src_word = word;
        src_send = 1'b1;
        @(negedge src_clk);
        src_send = 1'b0;
    endtask
    task automatic drain;
        @(negedge src_clk);
        while ((qhead != qtail) || (src_ready !== 1'b1)) @(negedge src_clk);
        repeat (2) @(negedge src_clk);
        require(qhead == qtail, "drain left an outstanding word");
    endtask
    task automatic pause_readout;
        @(negedge dst_clk);
        #0.002;
        dst_running = 1'b0;
    endtask
    task automatic qualify_analog;
        @(negedge src_clk);
        #1.337;
        analog_ready = 1'b1;
        wait (src_reset_n && dst_reset_n);
        @(negedge src_clk);
    endtask

    integer i, count_before, abort_before;
    initial begin
        repeat (4) @(negedge src_clk);
        $display("TEST boot: requests blocked while reset or analog-not-ready");
        offer(16'hDEAD);
        por_n = 1'b1;
        analog_power_good = 1'b1;
        offer(16'hBAD0);
        require(accepted_total == 0, "accepted before the analog-ready contract");

        $display("TEST normal: three coherent words");
        qualify_analog();
        send_when_ready(16'h007F); drain();
        send_when_ready(16'h0080); drain();
        send_when_ready(16'hA55A); drain();
        require(delivered_total == 3, "normal transfer count");

        $display("TEST rapid requests: busy requests rejected without overwriting data");
        @(negedge src_clk);
        src_send = 1'b1;
        for (i=0; i<24; i=i+1) begin
            prng = next_prng(prng);
            src_word = prng;
            @(negedge src_clk);
        end
        src_send = 1'b0;
        drain();
        require(rejected_total > 0, "rapid-request test did not exercise backpressure");

        $display("TEST clock pause: outstanding word survives until readout resumes");
        pause_readout();
        count_before = delivered_total;
        send_when_ready(16'hD00D);
        repeat (8) @(negedge src_clk);
        require(src_busy && delivered_total == count_before, "paused readout must hold transfer");
        dst_running = 1'b1;
        drain();
        require(delivered_total == count_before+1, "paused transfer delivered exactly once");

        $display("TEST power loss: in-flight word aborted with readout clock stopped");
        pause_readout();
        send_when_ready(16'hF001);
        repeat (3) @(negedge src_clk);
        require(qtail-qhead == 1, "power-loss test needs one outstanding word");
        abort_before = aborted_total;
        #0.002;
        analog_power_good = 1'b0;
        analog_ready = 1'b0;
        repeat (4) @(negedge src_clk);
        require(aborted_total == abort_before+1, "power loss abort count");
        analog_power_good = 1'b1;
        dst_running = 1'b1;
        count_before = accepted_total;
        offer(16'hBAD1);
        require(accepted_total == count_before, "power-good alone must not imply analog-ready");
        qualify_analog();
        send_when_ready(16'hBEEF); drain();

        $display("TEST ready withdrawal: coordinated reset, no stale replay after restart");
        pause_readout();
        send_when_ready(16'hF002);
        repeat (3) @(negedge src_clk);
        abort_before = aborted_total;
        #0.002;
        analog_ready = 1'b0;
        repeat (4) @(negedge src_clk);
        require(aborted_total == abort_before+1, "ready withdrawal abort count");
        dst_running = 1'b1;
        qualify_analog();
        send_when_ready(16'hC002); drain();

        $display("TEST external reset: clean empty-channel restart");
        @(negedge src_clk);
        #0.002;
        por_n = 1'b0;
        repeat (4) @(negedge src_clk);
        #1.337;
        por_n = 1'b1;
        wait (src_reset_n && dst_reset_n);
        send_when_ready(16'h1234); drain();

        require(qhead == qtail, "final scoreboard not empty");
        require(accepted_total == delivered_total+aborted_total, "accepted != delivered + aborted");
        require(aborted_total == 2, "expected exactly two deliberate in-flight aborts");
        require(delivered_total >= 8, "insufficient successful-transfer coverage");
        $display("RESULT accepted=%0d delivered=%0d aborted=%0d rejected_busy=%0d min_latency_ns=%0.3f max_latency_ns=%0.3f",
                 accepted_total, delivered_total, aborted_total, rejected_total, min_latency, max_latency);
        $display("PASS: all digital protocol assertions and directed tests passed");
        $fclose(trace_fd);
        $finish;
    end
    initial begin
        #200000;
        $fatal(1, "FAIL: watchdog timeout; protocol did not make progress");
    end
endmodule
