LAB 3 — SAMPLING SWITCHES AND REFERENCE LOADING
Open ../../lab_sampling_interface.html for the complete lesson.
From learning/: python labs/L03_sampling_interface/run.py
Needs Python/NumPy/Matplotlib and ngspice. See ../README.txt.
Default: run_results/; recorded evidence: results/.
Options: --ngspice /path/to/ngspice --models /path/to/wrapper --output /path/to/output
NGSPICE_BIN can also select the simulator.

57 acquisition cases: 54 combinations of ideal/NMOS/transmission-gate,
1k/10kOhm source,0.1/0.9/1.5V target and5/20/80ns acquisition; three m=8
parallel-copy TG cases at0.9V,1kOhm and20/80/200ns. TT25C1.8V,2pF sample.
NMOS W=.65,L=.15; HVT PMOS W=1,L=.15, numeric micrometres with scale=1u.
Acquisition is closing-ramp-start to opening-ramp-start, not fully-on time.
Pre-opening sample tOFF-50ps; post-edge tOFF+1ns; later hold tOFF+7ns.
Edge shift includes residual acquisition and modeled charge redistribution;
it is not an isolated channel-charge-injection measurement.
No transient noise or mismatch is enabled. kT/C in the lesson is analytical.

Three reference-load cases use assumed5Ohm,1nH,.2Ohm ESR,20/200/2000pF,
and a0.5mA pulse with2ns flat width and.2ns edges. NOT a characterized ADC.
Recovery: final entry into a50uV band after the pulse ends at12.4ns, judged
through80ns. First threshold crossings alone do not prove settling.
CSV/JSON, plots, all case decks/raw data/logs and a manifest are provided.
