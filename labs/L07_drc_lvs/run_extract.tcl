set magfile $::env(MAG)
set spicefile $::env(SPICE)
load $magfile
select top cell
extract path [file dirname $spicefile]
extract do local
extract unique
extract all
ext2spice lvs
ext2spice -o $spicefile
puts stdout "EXTRACTED $spicefile"
quit -noprompt
