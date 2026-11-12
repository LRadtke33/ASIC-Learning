#!/usr/bin/env python3
"""Characterize regenerative metastability of sky130_fd_sc_hd__dfxtp_1.

Schematic netlist, bundled SKY130 tt models, 25 C, 1.80 V, no layout parasitics.
Not a silicon reliability result and not a signoff MTBF.

Method A: sweep the D-edge to CLK-edge offset around the functional boundary,
measure clock-to-Q resolve time, and fit  T_r = tau * ln(T0 / |delta|)
on the polarity that produces a visible Q transition.

Method B: on a near-boundary trajectory, fit the exponential growth of the
master-latch differential  (a_634_159# - a_466_413#)  after the clock edge.

Run from learning/:  python labs/analysis_examples/metastability/run.py
Optional: --ngspice PATH  --output DIR
"""
from pathlib import Path
import argparse, hashlib, json, math, os, sys, time
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'common'))
from lab_support import (
    DEFAULT_MODELS, verify_models, executable, run_spice,
    data, crossing, relative_spice, metadata, plot_style,
)

CELL = HERE / 'sky130_fd_sc_hd__dfxtp_1.spice'
VDD = 1.80
TCLK = 2.0e-9
TRISE = 20e-12          # 0-100% of CLK and D
CLOAD = 1.678e-15       # Liberty D-pin capacitance of dfxtp_1 (following stage)
TCLK_50 = TCLK + TRISE / 2
INT_MASTER = ('a_466_413#', 'a_634_159#')   # master latch complementary nodes


def td_start_from_delta(delta):
    """PULSE delay so that D 50% occurs at TCLK_50 + delta."""
    return TCLK_50 + delta - TRISE / 2


def deck(td_start, tstop, maxstep, internals=False):
    models = relative_spice(DEFAULT_MODELS, HERE)  # will be rewritten per-folder
    cell = relative_spice(CELL, HERE)
    probe = 'v(CLK) v(D) v(Q)'
    if internals:
        probe += ' v("xq.a_466_413#") v("xq.a_634_159#") v("xq.a_891_413#") v("xq.a_1059_315#")'
    return f'''* sky130_fd_sc_hd__dfxtp_1 metastability
.lib "{{models}}" tt
.include "{{cell}}"
.temp 25
.options reltol=1e-7 abstol=1e-15 vntol=1e-9 method=gear maxord=2 rshunt=1e12
VDD VPWR 0 {VDD}
VSS VGND 0 0
VNB VNB 0 0
VPB VPB 0 {VDD}
VCLK CLK 0 PULSE(0 {VDD} {TCLK} {TRISE} {TRISE} 20n 40n)
VD D 0 PULSE(0 {VDD} {td_start} {TRISE} {TRISE} 20n 40n)
XQ CLK D VGND VNB VPB VPWR Q sky130_fd_sc_hd__dfxtp_1
CLOAD Q 0 {CLOAD}
.ic v(Q)=0
.control
set wr_vecnames
set wr_singlescale
set numdgt=16
tran {maxstep} {tstop} 1.8n {maxstep}
wrdata wave.dat {probe}
quit
.endc
.end
'''


def simulate(engine, out, td_start, tag, tstop=12e-9, maxstep=0.5e-12, internals=False):
    folder = out / 'decks' / tag
    folder.mkdir(parents=True, exist_ok=True)
    # paths relative to the deck folder
    models = relative_spice(DEFAULT_MODELS, folder)
    cell = relative_spice(CELL, folder)
    text = deck(td_start, tstop, maxstep, internals).replace('{models}', models).replace('{cell}', cell)
    # run_spice has a 120s timeout and flags 'error:' — our rshunt etc are fine
    # Use a local runner so we can detect "timestep too small" / aborted.
    import subprocess
    from spice_paths import portable_library_paths
    text = portable_library_paths(text, folder)
    (folder / 'bench.spice').write_text(text)
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = '1'
    p = subprocess.run([engine, '-b', 'bench.spice'], cwd=folder,
                       capture_output=True, text=True, timeout=180, env=env)
    log = p.stdout + '\n' + p.stderr
    (folder / 'ngspice.log').write_text(log)
    if p.returncode or 'aborted' in log.lower() or 'timestep too small' in log.lower() or 'fatal error' in log.lower():
        raise RuntimeError(f'ngspice failed in {folder}\n' + log[-2000:])
    raw = np.loadtxt(folder / 'wave.dat', skiprows=1)
    if raw.ndim != 2 or raw.shape[1] < 4 or not np.isfinite(raw).all():
        raise RuntimeError(f'bad wave data in {folder}, shape={getattr(raw, "shape", None)}')
    return raw


def crossings(t, y, level, rising=True, after=0.0):
    if rising:
        mask = (t[:-1] >= after) & (y[:-1] < level) & (y[1:] >= level)
    else:
        mask = (t[:-1] >= after) & (y[:-1] > level) & (y[1:] <= level)
    inds = np.flatnonzero(mask)
    return [float(t[k] + (level - y[k]) * (t[k + 1] - t[k]) / (y[k + 1] - y[k])) for k in inds]


def analyze(raw, tstop):
    t, clk, d, q = raw[:, 0], raw[:, 1], raw[:, 2], raw[:, 3]
    tclk = crossings(t, clk, VDD / 2, True)[0]
    td = crossings(t, d, VDD / 2, True)[0]
    qend = float(q[-1])
    qmax = float(q.max())
    t90 = crossings(t, q, 0.90 * VDD, True, after=tclk)
    t50 = crossings(t, q, 0.50 * VDD, True, after=tclk)
    t10 = crossings(t, q, 0.10 * VDD, True, after=tclk)
    if qend > 0.90 * VDD:
        res = 1
        tres90 = (t90[0] - tclk) if t90 else None
        tres50 = (t50[0] - tclk) if t50 else None
        tres10 = (t10[0] - tclk) if t10 else None
    elif qend < 0.10 * VDD:
        res = 0
        tres90 = tres50 = tres10 = None
    else:
        res = 'meta'
        tres90 = tres50 = tres10 = tstop - tclk
    return {
        'tclk': tclk, 'td': td, 'delta': td - tclk,
        'qend': qend, 'qmax': qmax, 'resolved': res,
        'tres_90': tres90, 'tres_50': tres50, 'tres_10': tres10,
    }


def binary_search_tm(engine, out, d_lo, d_hi, steps=20):
    """d_lo resolves to 1, d_hi resolves to 0. Return (tm, history)."""
    history = []
    for i in range(steps):
        mid = 0.5 * (d_lo + d_hi)
        raw = simulate(engine, out, td_start_from_delta(mid), f'bs{i:02d}', tstop=12e-9)
        a = analyze(raw, 12e-9)
        a['requested_delta'] = mid
        history.append(a)
        print(f"  bs{i:02d}  delta={a['delta']*1e15:14.4f} fs  Qend={a['qend']:.4f}  "
              f"res={a['resolved']}  tres90={fmt_ps(a['tres_90'])}", flush=True)
        if a['resolved'] == 1:
            d_lo = mid
        elif a['resolved'] == 0:
            d_hi = mid
        else:
            if a['qend'] >= 0.9:
                d_lo = mid
            else:
                d_hi = mid
    tm = 0.5 * (d_lo + d_hi)
    return tm, d_lo, d_hi, history


def fmt_ps(x):
    return '—' if x is None else f'{x*1e12:.2f} ps'


def linregress(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    sx, sy = x.sum(), y.sum()
    sxx, syy, sxy = (x * x).sum(), (y * y).sum(), (x * y).sum()
    den = n * sxx - sx * sx
    slope = (n * sxy - sx * sy) / den
    intercept = (sy - slope * sx) / n
    yhat = slope * x + intercept
    ss_res = ((y - yhat) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return float(slope), float(intercept), float(r2)


def method_b_fit(raw, tclk):
    """Exponential growth of master-latch differential after the clock."""
    t = raw[:, 0]
    n1, n2 = raw[:, 4], raw[:, 5]   # a_466, a_634 when internals=True
    # after clock + 80 ps (pass clock-path and initial slosh), before rails
    vdiff = n2 - n1
    # estimate Vm region: average of the two nodes while both are between 0.4 and 1.4
    mid = (n1 + n2) / 2
    # Use |vdiff| in 30-250 mV, t > tclk+80ps, and still heading away
    mask = (t > tclk + 80e-12) & (np.abs(vdiff) > 0.030) & (np.abs(vdiff) < 0.250)
    if mask.sum() < 20:
        return None
    tt = t[mask]
    vd = np.abs(vdiff[mask])
    # require monotonic growth of |vdiff| overall
    if vd[-1] <= vd[0]:
        return None
    slope, intercept, r2 = linregress(tt, np.log(vd))
    # ln|v| = ln|v0| + t/tau  =>  slope = 1/tau
    if slope <= 0:
        return None
    tau = 1.0 / slope
    return {
        'tau_s': tau,
        'r2': r2,
        'n_points': int(mask.sum()),
        't_window_s': [float(tt[0]), float(tt[-1])],
        'vdiff_window_V': [float(vd[0]), float(vd[-1])],
        'vm_mean_V': float(np.mean(mid[mask])),
    }


def mtbf_seconds(tres, tau, T0, fclk, fdata):
    """MTBF = exp(T_res/tau) / (T0 * fclk * fdata).  T_res and T0 consistent with Method A."""
    return math.exp(tres / tau) / (T0 * fclk * fdata)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ngspice')
    ap.add_argument('--output', type=Path, default=HERE / 'results')
    args = ap.parse_args()
    engine = executable(args.ngspice, 'NGSPICE_BIN', 'ngspice')
    verify_models()
    if not CELL.is_file():
        raise RuntimeError('Cell netlist missing: ' + str(CELL))
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # Nominal t_CQ: D well before the clock
    print('=== nominal t_CQ (D 200 ps before CLK) ===', flush=True)
    raw_nom = simulate(engine, out, td_start_from_delta(-200e-12), 'nominal', tstop=5e-9, maxstep=1e-12)
    nom = analyze(raw_nom, 5e-9)
    print(f"  t_CQ 10/50/90% = {fmt_ps(nom['tres_10'])} / {fmt_ps(nom['tres_50'])} / {fmt_ps(nom['tres_90'])}", flush=True)

    # Binary search the rising-D functional boundary (known bracket from exploration)
    print('=== binary search of rising-D boundary ===', flush=True)
    tm, lo, hi, hist = binary_search_tm(engine, out, -28.5e-12, -28.0e-12, steps=18)
    print(f"  t_m = {tm*1e12:.8f} ps   window = {(hi-lo)*1e18:.4f} as", flush=True)

    # Planned Method A offsets (resolve-to-1 side: D earlier than t_m, so delta = tm - offset)
    # Stay clear of numerical-noise offsets below ~0.02 fs for the published fit.
    offsets = np.array([
        2000, 1000, 500, 250, 150, 100, 60, 40, 25, 16, 10, 6, 4, 2.5, 1.5,
        1.0, 0.6, 0.4, 0.25, 0.15, 0.10, 0.06,
    ]) * 1e-15  # fs -> s
    print('=== Method A planned sweep ===', flush=True)
    rows = []
    for i, off in enumerate(offsets):
        delta = tm - off   # more negative than tm → resolve 1
        raw = simulate(engine, out, td_start_from_delta(delta), f'a{i:02d}', tstop=14e-9, maxstep=0.5e-12)
        a = analyze(raw, 14e-9)
        a['requested_offset_s'] = float(off)
        a['requested_delta'] = float(delta)
        a['offset_from_tm'] = float(a['delta'] - tm)
        rows.append(a)
        print(f"  a{i:02d}  |d-tm|={abs(a['delta']-tm)*1e15:10.4f} fs  res={a['resolved']}  "
              f"tres50={fmt_ps(a['tres_50'])}  tres90={fmt_ps(a['tres_90'])}", flush=True)

    # Fit on points that resolved to 1 with T_r well above nominal t_CQ
    # (exponential regeneration regime): tres_90 >= nominal + 80 ps, and |offset| >= 0.06 fs
    fit_rows = [r for r in rows
                if r['resolved'] == 1
                and r['tres_90'] is not None
                and r['tres_50'] is not None
                and r['tres_90'] >= nom['tres_90'] + 80e-12
                and abs(r['delta'] - tm) >= 0.05e-15]
    if len(fit_rows) < 6:
        raise RuntimeError(f'Not enough fit points ({len(fit_rows)})')

    def fit_kind(key):
        x = [math.log(1.0 / abs(r['delta'] - tm)) for r in fit_rows]
        y = [r[key] for r in fit_rows]
        slope, intercept, r2 = linregress(x, y)
        # T_r = tau * ln(1/|d|) + C  = tau * ln(T0/|d|)  =>  C = tau ln T0, T0=exp(C/tau)
        tau = slope
        T0 = math.exp(intercept / tau)
        return {'tau_s': tau, 'T0_s': T0, 'intercept_s': intercept, 'r2': r2,
                'n': len(fit_rows),
                'tres_range_s': [float(min(y)), float(max(y))],
                'offset_range_s': [float(min(abs(r['delta']-tm) for r in fit_rows)),
                                   float(max(abs(r['delta']-tm) for r in fit_rows))]}

    fit90 = fit_kind('tres_90')
    fit50 = fit_kind('tres_50')
    print(f"=== Method A fit (90%): tau={fit90['tau_s']*1e12:.3f} ps  T0={fit90['T0_s']*1e12:.4f} ps  R^2={fit90['r2']:.6f}", flush=True)
    print(f"=== Method A fit (50%): tau={fit50['tau_s']*1e12:.3f} ps  T0={fit50['T0_s']*1e12:.4f} ps  R^2={fit50['r2']:.6f}", flush=True)

    # Method B on a mid-range trajectory (aim ~600-800 ps resolve) + one shallower
    print('=== Method B internal-node fits ===', flush=True)
    b_results = []
    for tag, off in [('b600', 0.6e-15), ('b200', 2.5e-15), ('b080', 10e-15)]:
        raw = simulate(engine, out, td_start_from_delta(tm - off), tag,
                       tstop=14e-9, maxstep=0.25e-12, internals=True)
        a = analyze(raw, 14e-9)
        tclk = a['tclk']
        fb = method_b_fit(raw, tclk)
        entry = {'tag': tag, 'offset_s': off, 'analyze': a, 'fit': fb}
        b_results.append(entry)
        if fb:
            print(f"  {tag}  tres90={fmt_ps(a['tres_90'])}  tau_B={fb['tau_s']*1e12:.3f} ps  "
                  f"R^2={fb['r2']:.6f}  n={fb['n_points']}", flush=True)
        else:
            print(f"  {tag}  tres90={fmt_ps(a['tres_90'])}  Method B fit failed", flush=True)

    taus_b = [e['fit']['tau_s'] for e in b_results if e['fit'] and e['fit']['r2'] > 0.99]
    tau_b = float(np.mean(taus_b)) if taus_b else None
    print(f"  Method B mean tau = {tau_b*1e12:.3f} ps" if tau_b else '  Method B mean unavailable', flush=True)

    # Published tau: Method A at 90% (matches 'resolved to a valid level' idea).
    # Report Method B as confirmation.
    tau = fit90['tau_s']
    T0 = fit90['T0_s']

    # MTBF worked examples. T_res is the time from the capturing edge until the
    # second stage's setup requirement: T_period - t_setup.
    # Liberty setup (D rise, 0.01 ns / 0.01 ns) is 50.8281 ps — used here as a
    # documented constraint, not re-measured. For 20 ps edges we still use it
    # as a conservative budget item and state that.
    t_setup = 50.8281e-12
    examples = []
    cases = [
        # name, fclk, fdata (toggle rate), note
        ('50 MHz, 2-flop, f_data=5 MHz', 50e6, 5e6,
         'Typical student-design clock. Two-flop chain: T_res = T_clk - t_setup.'),
        ('50 MHz, 2-flop, f_data=25 MHz', 50e6, 25e6,
         'Same clock, higher asynchronous activity (data changes every 40 ns).'),
        ('200 MHz, 2-flop, f_data=20 MHz', 200e6, 20e6,
         'Faster clock, still a two-flop chain.'),
        ('500 MHz, 2-flop, f_data=50 MHz', 500e6, 50e6,
         'Aggressive for this library at 1.8 V; T_res shrinks with the period.'),
        ('50 MHz, one flop only (T_res = 0.4 ns)', 50e6, 5e6,
         'Illustrative single-stage aperture: only 400 ps allowed (not a 2-flop chain).'),
    ]
    for name, fclk, fdata, note in cases:
        period = 1.0 / fclk
        if 'one flop' in name:
            tres = 0.400e-9
        else:
            tres = period - t_setup
        m = mtbf_seconds(tres, tau, T0, fclk, fdata)
        examples.append({
            'name': name, 'fclk_Hz': fclk, 'fdata_Hz': fdata,
            'T_res_s': tres, 'T_period_s': period, 't_setup_s': t_setup,
            'MTBF_s': m, 'MTBF_years': m / (365.25 * 24 * 3600),
            'note': note,
        })
        years = m / (365.25 * 24 * 3600)
        print(f"  MTBF {name}: T_res={tres*1e9:.3f} ns  MTBF={m:.4e} s  ({years:.4e} y)", flush=True)

    # Sensitivity: extra resolution time multiplies MTBF by exp(dt/tau)
    sensitivity = {
        'extra_200ps_factor': math.exp(200e-12 / tau),
        'extra_one_FO4_72ps_factor': math.exp(72.15e-12 / tau),
        'one_more_flop_at_50MHz_factor': math.exp((20e-9) / tau),  # roughly one extra period
    }

    meta = metadata(engine, DEFAULT_MODELS, 'metastability_dfxtp_1')
    cell_sha = hashlib.sha256(CELL.read_bytes()).hexdigest()
    summary = {
        'conditions': {
            'cell': 'sky130_fd_sc_hd__dfxtp_1',
            'cell_spice_sha256': cell_sha,
            'cell_revision': 'ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1',
            'models': 'bundled sky130_course.lib.spice, tt, 25 C, 1.80 V',
            'clock_and_data_0_100_rise_s': TRISE,
            'load_F': CLOAD,
            'load_note': '1.678 fF = Liberty capacitance of the D pin of dfxtp_1 (a following synchronizer stage)',
            'layout_parasitics': False,
            'polarity': 'D 0-to-1 near the rising clock; Q was initialized to 0',
            'disclaimer': (
                'Schematic-level tt simulation of the published standard-cell netlist. '
                'No extracted parasitics, no mismatch, no voltage/temperature sweep. '
                'Not a silicon MTBF, not a signoff number, and not a foundry reliability limit.'
            ),
        },
        'nominal': nom,
        't_m_s': tm,
        't_m_window_s': [lo, hi],
        'binary_search': [{k: (float(v) if isinstance(v, (float, np.floating)) else v)
                           for k, v in h.items()} for h in hist],
        'method_a_points': [{k: (float(v) if isinstance(v, (float, np.floating)) else v)
                             for k, v in r.items()} for r in rows],
        'method_a_fit_90': fit90,
        'method_a_fit_50': fit50,
        'method_b': b_results,
        'method_b_mean_tau_s': tau_b,
        'published': {
            'tau_s': tau,
            'tau_source': 'Method A, clock-to-Q 90%, least-squares slope of T_r vs ln(1/|d-t_m|)',
            'T0_s': T0,
            'T_r_definition': 'Time from CLK 50% to Q 90%, including ordinary t_CQ',
            'MTBF_formula': 'exp(T_res/tau) / (T0 * f_clk * f_data)',
            'T_res_definition': 'For a two-flop chain, T_period - Liberty setup (D rise, 0.01 ns / 0.01 ns) = 50.8281 ps',
        },
        'mtbf_examples': examples,
        'sensitivity': sensitivity,
        'tool': meta,
        'runtime_s': time.time() - t0,
    }
    # numpy-safe json
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, Path):
            return str(o)
        raise TypeError(type(o))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, default=conv))
    print(f'wrote {out/"summary.json"}  runtime {time.time()-t0:.1f}s', flush=True)

    # Plots
    try:
        plt = plot_style()
        # 1) T_r vs ln(1/|offset|)
        fig, ax = plt.subplots(figsize=(7.2, 4.4))
        xs = [math.log(1.0 / abs(r['delta'] - tm)) for r in fit_rows]
        y90 = [r['tres_90'] * 1e12 for r in fit_rows]
        y50 = [r['tres_50'] * 1e12 for r in fit_rows]
        ax.plot(xs, y90, 'o', ms=6, label='T_r to Q 90%')
        ax.plot(xs, y50, 's', ms=5, label='T_r to Q 50%')
        xr = np.linspace(min(xs), max(xs), 50)
        ax.plot(xr, (fit90['tau_s'] * xr + fit90['intercept_s']) * 1e12, '-',
                label=f"90% fit  τ = {fit90['tau_s']*1e12:.2f} ps  R² = {fit90['r2']:.4f}")
        ax.plot(xr, (fit50['tau_s'] * xr + fit50['intercept_s']) * 1e12, '--',
                label=f"50% fit  τ = {fit50['tau_s']*1e12:.2f} ps  R² = {fit50['r2']:.4f}")
        ax.set_xlabel('ln(1 / |t_D − t_m|)')
        ax.set_ylabel('Resolve time from CLK 50% (ps)')
        ax.set_title('sky130_fd_sc_hd__dfxtp_1  —  Method A  (tt, 25 °C, 1.80 V)')
        ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig.savefig(out / 'method_a_fit.svg')
        fig.savefig(out / 'method_a_fit.png', dpi=140)
        plt.close(fig)

        # 2) A near-boundary waveform (use b600 internals if available)
        btag = out / 'decks' / 'b600' / 'wave.dat'
        if btag.is_file():
            raw = np.loadtxt(btag, skiprows=1)
            t = raw[:, 0]
            fig, axes = plt.subplots(2, 1, sharex=True, figsize=(7.2, 5.6),
                                     gridspec_kw={'height_ratios': [1.1, 1]})
            axes[0].plot(t * 1e9, raw[:, 1], label='CLK')
            axes[0].plot(t * 1e9, raw[:, 2], label='D')
            axes[0].plot(t * 1e9, raw[:, 3], label='Q')
            axes[0].set_ylabel('Voltage (V)')
            axes[0].legend(frameon=False, ncol=3, fontsize=9)
            axes[0].set_title('Near-boundary trajectory (Q delayed by regeneration)')
            if raw.shape[1] >= 6:
                axes[1].plot(t * 1e9, raw[:, 4], label='master a_466_413#')
                axes[1].plot(t * 1e9, raw[:, 5], label='master a_634_159#')
                axes[1].axhline(0.9, color='#999', lw=0.7, ls=':')
                axes[1].legend(frameon=False, fontsize=9)
                axes[1].set_ylabel('Voltage (V)')
            axes[1].set_xlabel('Time (ns)')
            axes[1].set_xlim(1.9, min(4.5, t[-1] * 1e9))
            fig.tight_layout()
            fig.savefig(out / 'waveform_near_boundary.svg')
            fig.savefig(out / 'waveform_near_boundary.png', dpi=140)
            plt.close(fig)
        print('wrote plots', flush=True)
    except Exception as e:
        print('plot failed:', e, flush=True)

    print('TAU_PS', tau * 1e12)
    print('T0_PS', T0 * 1e12)
    print('DONE')


if __name__ == '__main__':
    main()
