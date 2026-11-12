# Static IR + EM on Lab 6 SPM, nom_tt, OpenROAD PSM.
# Matches LibreLane irdrop.tcl: no activity override, no VSRC_LOC_FILES.
# Plus -enable_em, which Classic 3.0.17 irdrop.tcl does not pass.

set RUN /workspace/eda/runs/spm/runs/RUN_2026-11-11_16-09-06
set OUT /tmp/lab6_ir
set LIB /workspace/eda/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
set SDC $RUN/final/sdc/spm.sdc

read_db $RUN/final/odb/spm.odb
read_liberty $LIB
read_sdc $SDC
read_spef $RUN/final/spef/nom/spm.nom.spef

set_pdnsim_net_voltage -net VPWR -voltage 1.80
analyze_power_grid -net VPWR -voltage_file $OUT/net-VPWR.csv -enable_em -em_outfile $OUT/em-VPWR.txt

set_pdnsim_net_voltage -net VGND -voltage 0
analyze_power_grid -net VGND -voltage_file $OUT/net-VGND.csv -enable_em -em_outfile $OUT/em-VGND.txt

puts "==== DONE ===="
