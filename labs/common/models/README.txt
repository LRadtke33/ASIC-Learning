SELECTED SKY130 MODEL FILES FOR TEACHING LABS

Source: google/skywater-pdk-libs-sky130_fd_pr
Revision: f62031a1be9aefe902d6d54cddd6f59b57627436
License: Apache 2.0; see upstream/LICENSE and retained file headers.

Entry point: sky130_course.lib.spice
Syntax: .lib "path/to/sky130_course.lib.spice" tt
Supported sections: tt, ff, ss.
Devices: sky130_fd_pr__nfet_01v8 and sky130_fd_pr__pfet_01v8_hvt.

The upstream model files are unchanged. The course wrapper selects only these
two devices, their corner files and deterministic mismatch parameter definitions.
It applies .option scale=1u and the two zero rotation-delta parameters used by the
upstream models/all.spice. Width/length arguments are NUMBERS IN MICROMETRES:
  XN d g s b sky130_fd_pr__nfet_01v8 w=0.65 l=0.15
Do not append 'u' to these instance dimensions: that would scale twice.
Check supported geometry bins before changing dimensions. Pin order is d g s b.

source_manifest.json records exact source URLs and SHA-256 hashes. The lab
scripts verify these bytes; they do not silently update the model revision.

This selected model set is not a complete PDK installation. It does not contain
layout rules, device generators, layout-dependent extraction, qualification,
all device families, or a validated statistical mismatch flow. Do not infer
reliability limits, manufacturing acceptance or yield from these lab runs.
Reproduce implementation work in the PDK/tool setup selected for your project.
