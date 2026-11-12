# MAG, GDS, CELL from env
load $::env(MAG)
select top cell
# Write GDS of the loaded layout (not a library abstract)
cif *hier write disable
cif *array write disable
gds write $::env(GDS)
puts stdout "WROTE $::env(GDS)"
quit -noprompt
