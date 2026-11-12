# OpenSTA 2.7 — cell-delay SDF for the Yosys-mapped gray4 netlist, tt 25 C 1.80 V.
set lib $::env(LIB)
set netlist $::env(NETLIST)
set sdfout $::env(SDFOUT)
read_liberty $lib
read_verilog $netlist
link_design gray4
create_clock -name clk -period 10 [get_ports clk]
set_input_delay -clock clk 0 [all_inputs]
set_output_delay -clock clk 0 [all_outputs]
set_input_transition 0.05 [all_inputs]
report_checks -path_delay max -fields {slew cap input_pins net} -digits 4
report_checks -path_delay min -fields {slew cap input_pins net} -digits 4
report_worst_slack -max
report_worst_slack -min
write_sdf $sdfout
puts "WROTE_SDF $sdfout"
