#!/usr/bin/env python3
"""Liberty-based numbers for lessons 27 and 34 (no simulator needed).
Reads the bundled sky130_fd_sc_hd__tt_025C_1v80.lib (labs/L05.../reference), then:
  1. fits an effective resistance and intrinsic delay to inv_1..inv_8 delay-vs-load rows,
  2. reads inv_1 delay versus fanout,
  3. times a scan-flop register-to-register path with slew propagation, and its scan-shift hold path.
Run from learning/:  python labs/analysis_examples/delay_physics/liberty_path.py
"""
from pathlib import Path
import json, re
import numpy as np
HERE = Path(__file__).resolve().parent
LIB = HERE.parent.parent / 'L05_mixed_signal_integration/reference/sky130_fd_sc_hd__tt_025C_1v80.lib'
TXT = LIB.read_text()

def block(text, start):
    i = text.index('{', start); depth = 0
    for j in range(i, len(text)):
        if text[j] == '{': depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0: return text[i + 1:j]
    raise ValueError

def cell(name):
    return block(TXT, TXT.index(f'cell ("sky130_fd_sc_hd__{name}")'))

def groups(text, kind):
    out = []
    for m in re.finditer(r'\b' + kind + r'\s*\(\s*"?([^")]*)"?\s*\)\s*\{', text):
        # only direct children: skip if inside a deeper block is not checked; fine for pin/timing use here
        out.append((m.group(1), block(text, m.start())))
    return out

def attr(text, key):
    m = re.search(r'\b' + key + r'\s*:\s*"?([^";]+)"?\s*;', text)
    return m.group(1).strip() if m else None

def table(text, name):
    m = re.search(r'\b' + name + r'\s*\(\s*"?([^")]*)"?\s*\)\s*\{', text)
    if not m: return None
    b = block(text, m.start())
    nums = lambda s: [float(x) for x in s.replace('\\', '').replace('"', '').replace('\n', ' ').split(',') if x.strip()]
    i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', b).group(1))
    i2m = re.search(r'index_2\s*\(\s*"([^"]*)"', b); i2 = nums(i2m.group(1)) if i2m else None
    vals = re.search(r'values\s*\((.*?)\)\s*;', b, re.S).group(1)
    rows = [nums(r) for r in re.findall(r'"([^"]*)"', vals)]
    return dict(i1=i1, i2=i2, v=rows)

def lookup(t, x1, x2=None):
    """Bilinear interpolation (linear extrapolation is refused) on a Liberty table."""
    xs = np.array(t['i1']); z = np.array(t['v'])
    if t['i2'] is None or z.shape[0] == 1 and len(t['i1']) != 1:
        return float(np.interp(x1, xs, z.ravel()))
    ys = np.array(t['i2'])
    assert xs[0] <= x1 <= xs[-1] and ys[0] <= x2 <= ys[-1], (x1, x2)
    return float(np.interp(x1, xs, [np.interp(x2, ys, row) for row in z]))

def pin(cellname, pinname):
    for n, b in groups(cell(cellname), 'pin'):
        if n == pinname: return b
    raise KeyError(pinname)

def cap(cellname, pinname):
    return float(attr(pin(cellname, pinname), 'capacitance'))

def arcs(cellname, outpin):
    res = []
    for _, tb in groups(pin(cellname, outpin), 'timing'):
        res.append(dict(related=attr(tb, 'related_pin'), type=attr(tb, 'timing_type') or 'combinational',
                        sense=attr(tb, 'timing_sense'), txt=tb))
    return res

def arc(cellname, outpin, related, ttype=None):
    for a in arcs(cellname, outpin):
        if a['related'] == related and (ttype is None or a['type'] == ttype): return a['txt']
    raise KeyError((cellname, outpin, related, ttype))

def stage(cellname, outpin, related, in_slew, load_pf, out_edge):
    t = arc(cellname, outpin, related)
    d = lookup(table(t, 'cell_' + out_edge), in_slew, load_pf)
    s = lookup(table(t, out_edge + '_transition'), in_slew, load_pf)
    return d, s

def constraint(cellname, dpin, ttype, clk_slew, d_slew, d_edge):
    t = arc(cellname, dpin, 'CLK', ttype)
    return lookup(table(t, d_edge + '_constraint'), clk_slew, d_slew)

def main():
    R = {'library': LIB.name, 'units': 'ns, pF, nW (from the library header)'}
    # 1. effective resistance fits at the fastest input slew row (0.01 ns), loads 2..4 of the 7 columns
    fits = {}
    for c in ('inv_1', 'inv_2', 'inv_4', 'inv_8'):
        t = arc(c, 'Y', 'A'); out = dict(cin_fF=cap(c, 'A') * 1e3, leakage_nW=float(attr(cell(c), 'cell_leakage_power')))
        for edge in ('rise', 'fall'):
            tb = table(t, 'cell_' + edge); loads = np.array(tb['i2']); row = np.array(tb['v'][0])
            k = slice(2, 5)  # 3.57, 9.52, 25.4 fF
            slope, icpt = np.polyfit(loads[k], row[k], 1)
            out[edge] = dict(slope_kohm_per_0p69=slope / 0.69, reff_kohm=slope / 0.69, intrinsic_ps=icpt * 1e3,
                             c_self_fF=icpt / slope * 1e3)
        fits[c] = out
    R['reff_fits'] = fits
    # 2. inv_1 delay vs fanout of inv_1 loads, input slew 0.05 ns
    t = arc('inv_1', 'Y', 'A'); cin = cap('inv_1', 'A')
    R['fanout_liberty'] = [dict(n=n, load_fF=n * cin * 1e3, rise_ps=lookup(table(t, 'cell_rise'), 0.05, n * cin) * 1e3,
                                fall_ps=lookup(table(t, 'cell_fall'), 0.05, n * cin) * 1e3) for n in (1, 2, 4, 8, 16, 32)]
    # 3. register-to-register path with a scan flop at each end
    W = 0.0847e-3  # pF per um, minimum met1, HD tech LEF (lesson 26)
    wire_um = 20.0  # assumed short local route on every net
    clk_slew = 0.10  # ns, assumed clock transition at the flop pins after CTS
    lat_launch, lat_capture = 0.420, 0.470  # ns, assumed clock latencies from CTS
    period = 1.0
    path = [('sdfxtp_1', 'Q', 'CLK'), ('nand2_1', 'Y', 'A'), ('inv_1', 'Y', 'A'), ('nor2_1', 'Y', 'A'), ('buf_2', 'X', 'A')]
    sinks = [('nand2_1', 'A'), ('inv_1', 'A'), ('nor2_1', 'A'), ('buf_2', 'A'), ('sdfxtp_1', 'D')]
    # explicit, readable edge bookkeeping
    R['path'] = []
    for q_edge in ('rise', 'fall'):
        edges = [q_edge]
        for c in ('nand2_1', 'inv_1', 'nor2_1'):
            edges.append('fall' if edges[-1] == 'rise' else 'rise')
        edges.append(edges[-1])  # buf_2 non-inverting
        slew = clk_slew; arrival = lat_launch; rows = []
        for (c, o, rel), (sc, sp), e in zip(path, sinks, edges):
            load = cap(sc, sp) + wire_um * W
            d, s = stage(c, o, rel, slew, load, e)
            rows.append(dict(cell=c, arc=f'{rel}->{o}', out_edge=e, in_slew_ns=round(slew, 5), load_fF=round(load * 1e3, 4),
                             delay_ns=round(d, 5), out_slew_ns=round(s, 5)))
            arrival += d; slew = s
        d_edge = edges[-1]
        tsu = constraint('sdfxtp_1', 'D', 'setup_rising', clk_slew, slew, d_edge)
        th = constraint('sdfxtp_1', 'D', 'hold_rising', clk_slew, slew, d_edge)
        required = period + lat_capture - tsu
        R['path'].append(dict(q_edge=q_edge, d_edge=d_edge, stages=rows, data_arrival_ns=arrival, data_slew_ns=slew,
                              setup_ns=tsu, hold_ns=th, setup_required_ns=required, setup_slack_ns=required - arrival,
                              hold_slack_ns=arrival - (lat_capture + th), logic_ns=arrival - lat_launch - rows[0]['delay_ns']))
    R['path_assumptions'] = dict(period_ns=period, clk_slew_ns=clk_slew, launch_latency_ns=lat_launch, capture_latency_ns=lat_capture,
                                 skew_ns=lat_capture - lat_launch, wire_um_per_net=wire_um, wire_pf_per_um=W,
                                 side_inputs='nand2_1 B tied high, nor2_1 B tied low (non-controlling)', uncertainty_ns=0.0)
    # scan shift path: Q of one flop straight into SCD of the next, 20 um wire, same skew
    sh = []
    for e in ('rise', 'fall'):
        load = cap('sdfxtp_1', 'SCD') + wire_um * W
        d, s = stage('sdfxtp_1', 'Q', 'CLK', clk_slew, load, e)
        th = constraint('sdfxtp_1', 'SCD', 'hold_rising', clk_slew, s, e)
        tsu = constraint('sdfxtp_1', 'SCD', 'setup_rising', clk_slew, s, e)
        sh.append(dict(edge=e, clk_to_q_ns=d, q_slew_ns=s, scd_hold_ns=th, scd_setup_ns=tsu,
                       hold_slack_ns=lat_launch + d - (lat_capture + th)))
    R['scan_shift_hold'] = sh
    R['sce_constraints_clk0p1'] = {f'{e}_{ds}': dict(setup_ns=constraint('sdfxtp_1', 'SCE', 'setup_rising', clk_slew, ds, e),
                                               hold_ns=constraint('sdfxtp_1', 'SCE', 'hold_rising', clk_slew, ds, e))
                                 for e in ('rise', 'fall') for ds in (0.05, 0.5)}
    R['d_setup_compare_clk0p1_d0p03'] = {c: dict(rise=constraint(c, 'D', 'setup_rising', clk_slew, 0.03, 'rise'), fall=constraint(c, 'D', 'setup_rising', clk_slew, 0.03, 'fall'))
                                         for c in ('dfxtp_1', 'sdfxtp_1')}
    R['clk_to_q_compare_4fF'] = {c: dict(rise=stage(c, 'Q', 'CLK', clk_slew, 0.004, 'rise')[0], fall=stage(c, 'Q', 'CLK', clk_slew, 0.004, 'fall')[0]) for c in ('dfxtp_1', 'sdfxtp_1')}
    R['pins_fF'] = {f'{c}.{p}': cap(c, p) * 1e3 for c, p in [('inv_1', 'A'), ('nand2_1', 'A'), ('nor2_1', 'A'), ('buf_2', 'A'),
                                                         ('dfxtp_1', 'D'), ('dfxtp_1', 'CLK'), ('sdfxtp_1', 'D'), ('sdfxtp_1', 'SCD'), ('sdfxtp_1', 'SCE'), ('sdfxtp_1', 'CLK')]}
    R['leakage_nW'] = {c: float(attr(cell(c), 'cell_leakage_power')) for c in ('inv_1', 'inv_4', 'inv_8', 'buf_2', 'nand2_1', 'nor2_1', 'dfxtp_1', 'sdfxtp_1')}
    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'liberty_summary.json').write_text(json.dumps(R, indent=1))
    print(json.dumps(R, indent=1)[:6000])

if __name__ == '__main__':
    main()
