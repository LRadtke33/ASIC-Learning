`ifdef FORMAL
    reg f_past_valid = 1'b0;
    always @(posedge clk) f_past_valid <= 1'b1;

    // Mutual exclusion and count consistency.
    always @(*) begin
        assert (!(full && empty));
        assert (full  == (count == 3'd4));
        assert (empty == (count == 3'd0));
        assert (count <= 3'd4);
    end

    // Occupancy evolves only on accepted writes / reads.
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

    // Write-to-full is ignored: occupancy stays 4.
    always @(posedge clk) begin
        if (f_past_valid && $past(rst_n) && rst_n && $past(full) && $past(wr) && !$past(rd))
            assert (count == 3'd4 && full);
    end

    always @(posedge clk) begin
        if (!rst_n) assert (empty && !full && count == 3'd0);
    end

    // Covers: fill to full, drain to empty, simultaneous wr/rd at mid-fill.
    always @(posedge clk) cover (full);
    always @(posedge clk) cover (f_past_valid && $past(full) && empty);
    always @(posedge clk) cover (f_past_valid && rst_n && $past(wr) && $past(rd) && $past(count) == 3'd2);
`endif
