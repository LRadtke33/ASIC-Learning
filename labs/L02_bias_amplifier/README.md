# Lab 2 — Bias, Gain and Startup

Open `../../lab_bias_amplifier.html` for the illustrated step-by-step lesson. This directory contains the runnable experiments and their captured evidence.

## Reproduce the experiments

Requirements: Python 3.10 or later (standard library only), ngspice on PATH or specified explicitly, and the sibling `../common/models/` directory supplied with the course.

```sh
cd learning/labs/L02_bias_amplifier
python3 run_lab.py
```

An explicit simulator path or environment variable is supported:

```sh
python3 run_lab.py --ngspice /absolute/path/to/ngspice
NGSPICE_BIN=/absolute/path/to/ngspice python3 run_lab.py
```

The default output is `run_results/`. The captured `results/` directory is preserved unless you explicitly select it with `--output`. Running all nominal experiments generates 41 ngspice decks: two mirror sweeps, an amplifier transfer sweep, 23 bias-calibration points, the unclamped operating point, four finite-difference cases, two AC sweeps, two transient cases, and six behavioral startup experiments.

The default model wrapper is resolved relative to this script, not the current working directory:

```text
../common/models/sky130_course.lib.spice
```

Override it using `--models /path/to/compatible/library.spice`. Generated decks have relative model paths. To rerun a single deck with no Python, enter its output directory and run `ngspice -b mirror_long.cir`. This overwrites that deck's raw data; use a sibling copy of the results directory for manual experiments.

## Captured conditions and actual results

The supplied snapshot was actually executed with ngspice 44.2 on 6 November 2026. MOS simulations use TT, 25 °C, VDD = 1.8 V and ideal 20 µA reference-current sources. Exact UTC time, simulator executable hash, Python version, model/deck/raw/CSV hashes and source-file verification appear in `results/provenance.json`.

- Long NMOS mirror, W/L = 5/1 µm: 20.1921 µA at VOUT = 0.900 V; sampled ±5% current-accuracy interval 0.285–1.570 V.
- Short NMOS mirror, W/L = 5/0.15 µm: 23.3856 µA at VOUT = 0.900 V; sampled ±5% interval 0.650–0.760 V.
- Calibrated amplifier bias: VIN = 0.757010794 V and unclamped VOUT = 0.900000259 V.
- Common-source gain: −105.3997 V/V at 10 Hz, consistent with the independently measured DC derivatives.
- First −3 dB frequencies: 314.16 kHz with 1 pF and 31.63 kHz with 10 pF.
- At 10 kHz, a 0.5 mV input amplitude produces 0.847293–0.952550 V output. A 50 mV input is strongly compressed, with 0.09684–1.70254 V output.
- The separate behavioral startup model stays off from zero without a kick; a state-qualified kick recovers after the tested brownout, while an initial-only kick does not.

`metrics.json` gives more digits and extraction definitions. `checks.json` records the limited consistency checks. These are numerical results for the specified models and circuits, not silicon measurements or manufacturing guarantees.

## Model and geometry conventions

The selected primitive models are pinned to:

```text
https://github.com/google/skywater-pdk-libs-sky130_fd_pr/tree/f62031a1be9aefe902d6d54cddd6f59b57627436
```

The wrapper includes `.option scale=1u`, so the instance arguments in these decks are numbers in micrometres: `w=5 l=1`, **without** a `u` suffix. The wrapper supports `tt`, `ff` and `ss`. It selects `sky130_fd_pr__nfet_01v8` and `sky130_fd_pr__pfet_01v8_hvt`; it is not a complete PDK installation. The upstream license and source manifest are in the common model directory.

These model files have geometry bins. WN = 5 µm with L = 1 or 0.15 µm, and WP = 7 µm with L = 1 µm, were chosen from supported bins. An arbitrary geometry edit may not be supported by this selected model preparation. Source/drain areas and perimeters assume a 0.29 µm diffusion extension: NMOS AD = AS = 1.45 µm², PD = PS = 10.58 µm; PMOS AD = AS = 2.03 µm², PD = PS = 14.58 µm. These are schematic assumptions, not DRC-checked or extracted layout geometry.

## Suggested extensions — not additional supplied results

```sh
python3 run_lab.py --corner ff --bias 0.757010794 --output run_ff_fixed
python3 run_lab.py --corner ss --temperature 85 --bias 0.757010794 --output run_ss_85_fixed
python3 run_lab.py --corner ss --temperature 85 --output run_ss_85_centered
python3 run_lab.py --behavioral-only --output run_startup
```

Omitting `--bias` recalibrates the amplifier input at each condition to center the output near 0.9 V. A fixed input tests bias robustness; the two experiments answer different questions. A fixed-bias stage may move toward a rail, making a nominal linear-gain comparison inappropriate. Inspect the operating point and logs before interpreting failed checks.

## Startup model scope

`circuits/startup_behavioral.cir.in` contains no SKY130 transistors, BJTs or physical bandgap. It represents a normalized bias state with a one-state nonlinear ODE:

```text
tau dx/dt = x(x - 0.3)(1 - x),  tau = 50 us
```

This expression applies at full supply with no kick. Supply qualification, low-supply discharge and a separate 5 µA behavioral startup kick are added explicitly. A 1 nF capacitor represents the state; it is not extracted circuit capacitance. The ideal displayed reference is limited to the supply range. Explicit initial states and `uic` make the startup assumption visible. The six cases include no startup, favorable initialization, fast/slow ramps and two brownout recovery strategies. First 99% threshold crossings are comparison markers, not physical reference-ready specifications.

## What is not covered

No extracted interconnect, mismatch Monte Carlo, noise, transistor-level reference circuit, physical startup implementation, layout verification or silicon correlation is claimed. The nominal results do not establish yield, reliability or a complete analog IP block. The AC stage phase is not a feedback-loop return ratio, and the large transient amplitude ratio is not a linear gain or THD result.

Generated `.cir`, `.log`, `.dat` and `.csv` files preserve the evidence. SVG charts are produced directly from captured numerical data by the runner. The course's diagrams and Python/SPICE testbenches are teaching material; the upstream model license remains in `../common/models/upstream/LICENSE`.
