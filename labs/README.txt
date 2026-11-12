ASIC DESIGN TEACHING LABS — SETUP AND REPRODUCTION
Edition: 11 November 2026 (67 lessons + 7 labs)

START HERE
Extract the complete ZIP, then open learning/index.html in a browser.
The HTML, diagrams, plots, recorded results, and source files work offline.
Open learning/labs.html for the guided lab directory and prerequisites.
Do not open HTML directly inside the ZIP: relative assets need extraction.

The package includes executed simulation records, not only proposed exercises.
Each lab explains the model level, measurements, results, and limitations.
The course is educational; it is not a qualified PDK or a signoff flow.

FOLDERS AND ENTRY POINTS (from the learning/ directory)
1  python labs/L01_inverter/run.py
2  python labs/L02_bias_amplifier/run_lab.py
3  python labs/L03_sampling_interface/run.py
4  python labs/L04_layout_extraction/run_lab.py --engine ngspice
5  python labs/L05_mixed_signal_integration/run.py
   python labs/analysis_examples/run.py
   python labs/L05_mixed_signal_integration/synthesis_example/run_synthesis.py

6  Lab 6, RTL to GDS, is documented in learning/lab_rtl_to_gds.html.
   Sources: labs/L06_rtl_to_gds/. Recorded metrics: labs/analysis_examples/rtl_to_gds/.
   Requires LibreLane 3.0.17 and a sky130A PDK; it is not part of run_all.py.
7  Lab 7, DRC and LVS debug, is documented in learning/lab_drc_lvs.html.
   Layouts and scripts: labs/L07_drc_lvs/. Requires Magic, KLayout, Netgen and the PDK;
   it is not part of run_all.py. Antenna theory is lesson 41, not repeated in this lab.



A convenience runner executes labs 1–5 plus the trim/FFT calculations (labs 6 and 7 need LibreLane / Magic and are run separately):
   python labs/run_all.py
Optional synthesis:
   python labs/run_all.py --include-synthesis
Subset:
   python labs/run_all.py --labs 1 3 analysis

INSTALLED SOFTWARE
Reference execution: Linux, Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0,
Matplotlib 3.10.8, ngspice 44.2, Icarus Verilog 12.0, Yosys 0.52 with ABC.
Python 3.11/3.12 is a practical starting point. Other compatible versions may
work, but the recorded runs establish only the versions listed above.

Use an existing environment or create a Python virtual environment:
   python -m venv .venv
   . .venv/bin/activate
   python -m pip install -r labs/common/requirements.txt

Install ngspice for Labs 1–3 and the SPICE mode of Lab 4.
Install Icarus Verilog (iverilog and vvp) for Lab 5.
Install Yosys with ABC only for the optional synthesis/equivalence example.
Use your operating system's package manager or the projects' official packages:
   https://ngspice.sourceforge.io/download.html
   https://steveicarus.github.io/iverilog/usage/installation.html
   https://yosyshq.readthedocs.io/projects/yosys/en/latest/getting_started/installation.html
Linux or a Linux environment in WSL is recommended for the common toolchain.
Native Windows/macOS tool installations and browser-specific behavior were not
tested in this revision. Installing prerequisites may require a network.
Once installed, all default lab runs use bundled local source/model references.

Do not copy the scratch paths used in the recorded logs into your commands.
Pass your own tool paths if tools are not on PATH:
   python labs/run_all.py --ngspice /path/to/ngspice --iverilog /path/to/iverilog --vvp /path/to/vvp
   python labs/run_all.py --include-synthesis --yosys /path/to/yosys --abc /path/to/abc
Each individual runner has --help and an adjacent README.

RESULTS AND SAFE RERUNS
results/ contains the recorded evidence supplied with the course.
Default new runs write run_results/, preserving results/.
Rerunning into the same output folder replaces generated files in that folder.
For Labs 1–4 and analysis_examples, --output selects another folder; consult
each runner's --help for whether relative paths are relative to the current
directory or the lab directory. Use an absolute path when in doubt.
Lab 5 writes its known run_results folder and has explicit case selection.
The optional negative control creates a broken copy; it does not edit the RTL.

Logs, decks, CSVs and summaries remain together. A successful run proves only
the implemented checks under the stated model and stimulus. Review the plots,
measurements and assumptions, not only a process exit code.

WHAT IS REALLY SIMULATED
Lab 1: 18 combinations, each with actual transistor DC and transient analysis.
       Unmodified SKY130 HD inverter source netlist; schematic, not extracted.
Lab 2: 41 actual SPICE cases: 35 MOS bias/mirror/amplifier cases (including
       calibration and derivatives) plus six explicitly behavioral startup cases.
Lab 3: 57 acquisition simulations with ideal/MOS switches, and three assumed
       reference/package RLC simulations.
Lab 4: Four teaching geometries generate RC networks; eight actual SPICE
       transients, with finer-mesh/timestep and independent numerical checks.
       The geometry estimator is NOT a foundry-qualified layout extractor.
       Optional real-PDK DRC/LVS/PEX steps are described but were not executed.
Lab 5: Three self-checking digital clock configurations and a deliberate
       failing negative control; separately, actual SKY130 cell mapping and
       formal equivalence of a small enabled-XOR example.
       Logic simulation does not calculate analog metastability probability.
Analysis examples: deterministic trim calculations and seeded synthetic ADC
       records, FFT metrics and normalization checks. Not silicon data.

SKY130 REFERENCES AND UNITS
common/models/ contains selected unmodified primitive files, their license,
SHA-256 manifest and a small documented wrapper. This is not a full PDK.
Revision: f62031a1be9aefe902d6d54cddd6f59b57627436.
The wrapper selects tt/ff/ss for nfet_01v8 and pfet_01v8_hvt.
It sets scale=1u: instance w/l arguments are numeric micrometres without a
second u suffix. Supported geometry bins matter. Read models/README.txt.
The archived inverter, timing tables, and synthesis Liberty have separate
pinned revisions and local attribution. Do not assume all views are one
uniformly generated installed PDK. Their differences are part of the lesson.

LIMITS
No fabricated-silicon validation, qualified DRC/LVS/PEX, full-chip timing
closure, EM/reliability qualification, or validated statistical yield claim
is included. Startup reference dynamics and package/thermal examples are
explicit teaching models. Original course content and new examples remain
separate from third-party source licenses; retain those licenses and headers.

TROUBLESHOOTING
- Tool missing: run its version command, check PATH, or pass its full path.
- Model mismatch: compare source_manifest.json; restore the original ZIP.
  Do not silently update a model and claim the supplied numerical result.
- No supported device bin: use documented dimensions, or a complete compatible
  model environment with its own provenance.
- SPICE error: inspect the case's ngspice log and deck before changing tolerances.
- A case fails only after changing a physical parameter: examine whether its
  operating point or stated measurement is still meaningful.
- Plots differ after a software update: compare numerical CSVs, assumptions,
  tolerances and versions. SVG metadata is not a numerical invariant.


PATHS WITH SPACES
Default runs work when the extracted course directory contains spaces.
For a custom output/model path that puts spaces in a .lib directive, the
SPICE runners create a local model-directory symlink to work around ngspice44
parsing. Model bytes are unchanged. Keep the model filename itself free of
spaces. If symlinks are unavailable, use the default in-course output or
space-free model/output paths.
