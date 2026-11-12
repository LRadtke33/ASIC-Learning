LAB 1 — SKY130 INVERTER CHARACTERIZATION
Open ../../lab_inverter_characterization.html for the complete lesson.
From learning/: python labs/L01_inverter/run.py
Needs Python/NumPy/Matplotlib and ngspice. See ../README.txt.
Default: run_results/; recorded evidence: results/.
Options: --ngspice /path/to/ngspice --models /path/to/wrapper --output /path/to/output
NGSPICE_BIN can also select the simulator.

18 cases: TT/25C/1.8V, SS/100C/1.6V, FF/-40C/1.95V;
loads 3.56533, 9.52062, 50 fF; input20-80% slew10 or100 ps.
Each has DC and transient analysis. All crossings interpolate raw data.
Delay50% input to50% opposite output; slew20–80%; energy integral of
-VDD*i(VDD) over0..7ns, one complete output discharge/recharge cycle.
Source pin order: A VGND VNB VPB VPWR Y. Both body ties are explicit.
DC/transient waveforms, decks and ngspice logs are inside each case folder.
summary.csv/json retain measurements; run_manifest.json records tools/models.

reference/ source files are unmodified public SKY130 HD artifacts at
ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1. See source_manifest.json and
reference/LICENSE. The shared primitive models have a separate revision.
This two-device source netlist is not extracted layout and does not reproduce
the original Liberty characterization flow. The disagreement is discussed
explicitly. Selected conditions are not a complete PVT/yield qualification.
