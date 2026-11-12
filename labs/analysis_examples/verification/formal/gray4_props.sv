// Formal properties for gray4.  Included under `ifdef FORMAL.
// Written in the Yosys / SymbiYosys immediate-assertion style so the
// open-source frontend can consume them (full SVA is noted in the lesson).
`ifdef FORMAL
    // Past-valid flag: $past is meaningless on the first cycle.
    reg f_past_valid = 1'b0;
    always @(posedge clk) f_past_valid <= 1'b1;

    // Reset: after a cycle with rst_n low, gray is 0.
    always @(posedge clk) begin
        if (f_past_valid && !$past(rst_n))
            assert (gray == 4'b0000);
    end

    // Enable: a taken step has Hamming distance 1 (Gray code).
    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && $past(en))
            assert ($countones(gray ^ $past(gray)) == 4'd1);
    end

    // Enable off: the register is frozen.
    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && !$past(en))
            assert (gray == $past(gray));
    end

    // Encoding: gray is the reflected binary of bin.
    always @(*) begin
        assert (gray == (bin ^ (bin >> 1)));
    end

    // Cover: a full wrap, 0000 -> ... -> 1000 -> 0000, with enable held.
    // Tracked with a small cover sequence: reach 1000, then 0000, after reset release.
    reg f_seen_1000 = 1'b0;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) f_seen_1000 <= 1'b0;
        else if (gray == 4'b1000) f_seen_1000 <= 1'b1;
    end
    always @(posedge clk) begin
        cover (f_past_valid && f_seen_1000 && gray == 4'b0000 && rst_n);
    end
`endif
