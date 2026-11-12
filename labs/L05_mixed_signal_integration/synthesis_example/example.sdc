# Teaching assumptions for enabled_xor. Units follow the bundled Liberty:
# time = ns, capacitance = pF. This file was NOT used in the recorded synthesis
# run, and no STA result is supplied. Replace these assumptions for a real design.
create_clock -name core_clk -period 10.0 -waveform {0.0 5.0} [get_ports clk]
set_clock_uncertainty -setup 0.20 [get_clocks core_clk]
set_clock_uncertainty -hold 0.05 [get_clocks core_clk]
set data_in [get_ports {en a[0] a[1] b[0] b[1]}]
set data_out [get_ports {q[0] q[1]}]
if {[llength $data_in] != 5} {error "Expected five data input bits"}
if {[llength $data_out] != 2} {error "Expected two output bits"}
set_input_delay -clock core_clk -max 2.50 $data_in
set_input_delay -clock core_clk -min 0.40 $data_in
set_input_transition 0.10 $data_in
set_output_delay -clock core_clk -max 2.00 $data_out
set_output_delay -clock core_clk -min -0.20 $data_out
set_load 0.020 $data_out
# No false or multicycle exceptions are warranted merely because en exists.
