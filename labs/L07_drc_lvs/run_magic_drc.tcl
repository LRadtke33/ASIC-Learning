# Usage: magic -noconsole -dnull -rcfile $PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc run_magic_drc.tcl
# Set MAG and RPT from the environment.
set magfile $::env(MAG)
set rptfile $::env(RPT)
set cellname "sky130_fd_sc_hd__inv_1"

# Don't pull GDS from the PDK (we want this edited .mag, not the library GDS)
# The cell has a GDS_FILE property — clear after load by using mag, not gds.

drc euclidean on
drc off
load $magfile
# Detach from library GDS so our rectangles are what's checked
select top cell
# If the cell is a GDS abstract, we may need to remove GDS_FILE property
catch {property GDS_FILE}
catch {property GDS_FILE ""}
catch {property GDS_START ""}
catch {property GDS_END ""}

drc on
drc euclidean on
drc style drc(full)
select top cell
drc check
drc catchup

set fout [open $rptfile w]
puts $fout "cell: $cellname"
puts $fout "mag: $magfile"
set oscale [cif scale out]
set count 0
set drcresult [drc listall why]
foreach {errtype coordlist} $drcresult {
    puts $fout "RULE: $errtype"
    puts $fout "----------------------------------------"
    foreach coord $coordlist {
        set bllx [expr {$oscale * [lindex $coord 0]}]
        set blly [expr {$oscale * [lindex $coord 1]}]
        set burx [expr {$oscale * [lindex $coord 2]}]
        set bury [expr {$oscale * [lindex $coord 3]}]
        puts $fout [format "  box %g %g %g %g um" $bllx $blly $burx $bury]
        incr count
    }
    puts $fout ""
}
puts $fout "COUNT: $count"
puts stdout "DRC COUNT: $count  (written $rptfile)"
close $fout
quit -noprompt
