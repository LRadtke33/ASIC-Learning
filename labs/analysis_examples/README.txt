LESSONS 59 AND 60 — REPRODUCIBLE NUMERICAL EXAMPLES
Open ../../calibration_trim.html and ../../spectral_measurements.html.
From learning/: python labs/analysis_examples/run.py
Needs Python/NumPy/SciPy/Matplotlib; no SPICE, PDK or network needed.
Default writes run_results/; results/ is the supplied reference record.
--output selects a different directory.

Trim: ideal 6-bit code, 50 uV step, neutral 32; offset sweep and quadratic
example of remaining temperature curvature after endpoint correction.
FFT: seeded synthetic 4096-sample 14-bit ADC record, 1 MHz sampling,
67 coherent cycles; defined noise/harmonics, DC removal and single-sided
power normalization. No result represents a fabricated or simulated ASIC.
The runner checks Parseval, a pure sine, SciPy periodogram agreement,
periodic Hann CG/ENBW, and the trim half-step bound within correction range.
summary.json contains all assumptions and measured numerical metrics.
adc_record.csv and spectrum.csv make the signal and power calculation auditable.

Lessons 27 and 34 (delay physics and the timed path) have their own scripts and
recorded results in delay_physics/; see delay_physics/README.txt.

Lessons 32 and 30 have additional recorded tool results:

  labs/analysis_examples/metastability/  — ngspice Method A tau for dfxtp_1
      (lesson 32). See that folder’s README.txt; re-run with
      python labs/analysis_examples/metastability/run.py

  labs/analysis_examples/cts_spm/        — LibreLane 3.0.17 CTS reports for the
      bundled spm example (lesson 30). Mid-PnR, not a signoff result.
