// Incomplete case: infers a latch on next_state. For lint only, not for mapping.
module latch_pitfall(input [1:0] state, input tick, output reg [1:0] next_state);
    always @* begin
        case (state)
            2'd0: if (tick) next_state = 2'd1;
            2'd1: if (tick) next_state = 2'd2;
            // missing 2'd2 and default — latch
        endcase
    end
endmodule
