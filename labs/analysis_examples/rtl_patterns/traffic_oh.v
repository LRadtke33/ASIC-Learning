// Same machine, explicit one-hot encoding (one flop per state).
module traffic_oh (
    input  wire clk,
    input  wire rst_n,
    input  wire tick,
    output reg  [1:0] light
);
    localparam [2:0] S_RED = 3'b001, S_GREEN = 3'b010, S_YELLOW = 3'b100;
    reg [2:0] state, next_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= S_RED;
        else
            state <= next_state;
    end

    always @* begin
        next_state = state;
        case (state)
            S_RED:    if (tick) next_state = S_GREEN;
            S_GREEN:  if (tick) next_state = S_YELLOW;
            S_YELLOW: if (tick) next_state = S_RED;
            default:            next_state = S_RED;
        endcase
    end

    always @* begin
        case (state)
            S_RED:    light = 2'd0;
            S_GREEN:  light = 2'd1;
            S_YELLOW: light = 2'd2;
            default:  light = 2'd0;
        endcase
    end
endmodule
