`timescale 1ns/1ps
// Educational, one-entry, four-phase bundled-data mailbox.
// src_send/src_word are synchronous to src_clk. The receiver is always ready.
// Both protocol endpoints reset together when the qualified analog contract fails.
// RTL simulation validates this digital protocol, not analog metastability or STA.
module mixed_signal_mailbox #(
    parameter integer WIDTH = 16
) (
    input  wire                 src_clk,
    input  wire                 dst_clk,
    input  wire                 por_n,
    input  wire                 analog_power_good,
    input  wire                 analog_ready,
    input  wire                 src_send,
    input  wire [WIDTH-1:0]     src_word,
    output wire                 src_ready,
    output wire                 src_busy,
    output reg                  src_accept,
    output reg                  src_reject,
    output reg                  dst_valid,
    output reg  [WIDTH-1:0]     dst_word,
    output wire                 src_reset_n,
    output wire                 dst_reset_n
);
    // A logical contract model: inputs come from a qualified always-on supervisor.
    // This Boolean expression is not a transistor-level power-good/reset circuit.
    wire link_arst_n = por_n & analog_power_good & analog_ready;
    reset_release u_src_reset(.clk(src_clk), .arst_n(link_arst_n),
                              .reset_n(src_reset_n));
    reset_release u_dst_reset(.clk(dst_clk), .arst_n(link_arst_n),
                              .reset_n(dst_reset_n));

    localparam [1:0] IDLE = 2'd0, WAIT_ACK_HIGH = 2'd1, WAIT_ACK_LOW = 2'd2;
    reg [1:0] src_state;
    reg [WIDTH-1:0] mailbox_word;
    reg req_src;
    reg ack_dst;
    wire req_dst;
    wire ack_src;

    sync_bit u_req_sync(.clk(dst_clk), .reset_n(dst_reset_n),
                        .async_level(req_src), .synced_level(req_dst));
    sync_bit u_ack_sync(.clk(src_clk), .reset_n(src_reset_n),
                        .async_level(ack_dst), .synced_level(ack_src));

    assign src_ready = src_reset_n && (src_state == IDLE);
    assign src_busy = src_reset_n && (src_state != IDLE);

    always @(posedge src_clk or negedge src_reset_n) begin
        if (!src_reset_n) begin
            src_state    <= IDLE;
            mailbox_word <= {WIDTH{1'b0}};
            req_src      <= 1'b0;
            src_accept   <= 1'b0;
            src_reject   <= 1'b0;
        end else begin
            src_accept <= 1'b0;
            src_reject <= src_send && (src_state != IDLE);
            case (src_state)
                IDLE: if (src_send) begin
                    mailbox_word <= src_word;
                    req_src      <= 1'b1;
                    src_accept   <= 1'b1;
                    src_state    <= WAIT_ACK_HIGH;
                end
                WAIT_ACK_HIGH: if (ack_src) begin
                    req_src   <= 1'b0;
                    src_state <= WAIT_ACK_LOW;
                end
                WAIT_ACK_LOW: if (!ack_src) src_state <= IDLE;
                default: begin
                    src_state <= IDLE;
                    req_src   <= 1'b0;
                end
            endcase
        end
    end

    always @(posedge dst_clk or negedge dst_reset_n) begin
        if (!dst_reset_n) begin
            ack_dst   <= 1'b0;
            dst_valid <= 1'b0;
            dst_word  <= {WIDTH{1'b0}};
        end else begin
            dst_valid <= 1'b0;
            if (!req_dst) ack_dst <= 1'b0;
            else if (!ack_dst) begin
                // The source holds this bus until the acknowledgment completes.
                // Physical implementation must constrain its settling time.
                dst_word  <= mailbox_word;
                dst_valid <= 1'b1;
                ack_dst   <= 1'b1;
            end
        end
    end
endmodule
