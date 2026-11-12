# Implementation intent that digital simulation does not verify

This note is a review aid, not a ready-made signoff SDC. The testbench intentionally
uses ideal digital events without interconnect or metastability delay models.

1. **Clock relationships.** The source and destination clocks are treated as
   asynchronous for protocol purposes. Their testbench periods are scenario
   inputs, not a guaranteed hardware phase relationship. Define the real clocks,
   waveforms, uncertainties, and operating modes in the implementation flow.
2. **Synchronizer control paths.** `req_src` crosses into `u_req_sync.meta`; `ack_dst`
   crosses into `u_ack_sync.meta`. Resolve the actual mapped pin names. Restrict any
   asynchronous timing exception to the intended first-stage input. Keep each
   `meta` to `sync` path timed, direct, short, and protected against retiming or
   first-stage fanout. The attribute alone does not prove these conditions.
3. **Bundled data.** `mailbox_word` is held from acceptance until the full handshake
   returns to idle. The receiver captures only after its request synchronizer.
   In this RTL, the receiving register sees the synchronized request on a later
   edge, giving a nominal control latency of two to three destination periods
   after a source launch in zero-delay simulation. This is not permission for
   unlimited data routing delay. Set a conservative maximum data-path delay to
   the receiving register, including margins for request propagation, clocking,
   setup, and variation. Verify that clock-group/false-path priority does not
   suppress the intended bound. There is no per-bit data synchronizer.
4. **Reset domains.** One qualified asynchronous condition asserts both local
   reset-release chains. Each releases on its own clock. Verify asynchronous
   reset minimum width, recovery/removal, distribution, and the power validity of
   all controlling cells. The other domain must never continue a half-reset
   handshake as though its old protocol state remained valid.
5. **Power and analog readiness.** The supervisor is modeled as a clean Boolean
   contract. A real implementation needs its own hysteresis/filtering, supply
   thresholds, isolation, clamp polarity, always-on connectivity, and analog
   settling criteria. Those do not emerge from this Verilog.
6. **Receiver service.** The current receiver is always ready while active and
   consumes every `dst_valid` pulse. Add buffering or another ready/valid handshake
   before connecting a receiver that can stall independently of its clock.

A long blanket false path between both clock domains can hide the data-settling
requirement. A blanket reset false path can hide release violations. Review
exception coverage and report actual start/end pin collections rather than
assuming a command matched the intended signals.
