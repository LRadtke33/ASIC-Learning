// Concurrent SVA illustrating the same properties as gray4_formal.v.
// The open-source Yosys frontend we ran consumes immediate assertions
// (`assert (...)` inside an always block).  This file is for reading:
// it is the form a SystemVerilog simulator or a commercial formal tool
// would take.  It is not one of the recorded SymbiYosys runs.
module gray4_sva (input clk, rst_n, en, input [3:0] gray, bin);
    property p_reset;
        @(posedge clk) !rst_n |=> (gray == 4'b0000);
    endproperty
    property p_hamming;
        @(posedge clk) disable iff (!rst_n)
            en |=> ($countones(gray ^ $past(gray)) == 1);
    endproperty
    property p_hold;
        @(posedge clk) disable iff (!rst_n)
            !en |=> (gray == $past(gray));
    endproperty
    assert property (p_reset);
    assert property (p_hamming);
    assert property (p_hold);
    assert final (gray == (bin ^ (bin >> 1)));
endmodule
