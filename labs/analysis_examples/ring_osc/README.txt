11-STAGE inv_1 RING OSCILLATOR (lesson 32, clock generation)
============================================================
Recorded 11 November 2026, America/Chicago, with ngspice 44.2
(/usr/bin/ngspice). Course model library labs/common/models/sky130_course.lib.spice,
.lib tt, .temp 25. Each stage is the inv_1 device pair used in lesson 27
(NMOS sky130_fd_pr__nfet_01v8 W=0.65 um L=0.15 um, PMOS
sky130_fd_pr__pfet_01v8_hvt W=1.0 um L=0.15 um), instantiated as an X subcircuit
with .option scale=1u from the library. Schematic only: no cell-layout parasitics,
no extracted wiring.

The ring has 11 stages (odd). Node n1 is initialised at 0 V (.ic). After discarding
the first quarter of the transient, frequency is 1 / mean period between successive
VDD/2 rising crossings on n1. Stage delay is t_d = T / (2 N) with N = 11, which
is the definition behind f ≈ 1/(2 N t_d). This is a fanout-of-1 ring (each
inverter drives only the next), not an FO4 path.

VDD    period (ps)   f (MHz)    t_d (ps)   lesson-27 FO4 (ps), same models
1.00   5405.54        185.00     245.71     710.38
1.20   1788.46        559.14      81.29     234.97
1.40   1000.96        999.04      45.50     132.16
1.60    695.23       1438.37      31.60      92.33
1.80    540.79       1849.14      24.58      72.15
1.95    469.44       2130.18      21.34      (not in the lesson-27 sweep)

FO4 values are from labs/analysis_examples/delay_physics/results/spice_summary.json,
re-run 11 November 2026, ngspice 44.2, as cited in lesson 27. This ring was not
used to produce those FO4 numbers.

A noiseless schematic has no period jitter to report; period-to-period variation
in this data is below the measurement granularity and is not a silicon jitter
figure.

Re-run (stdlib only): python3 run.py
Results: ring_osc.json; decks in decks/.
