#!/usr/bin/env python3
"""Delay-physics examples for lessons 27 and 34: SKY130 device curves, effective resistance,
fanout, FO4, wire + via RC chains, repeaters, and supply-voltage energy/delay.
Uses the bundled SKY130 tt models (nfet_01v8, pfet_01v8_hvt). Run from learning/:
    python labs/analysis_examples/delay_physics/run.py [--ngspice PATH]
"""
from pathlib import Path
import argparse, json
import numpy as np
from sim_lib import HERE, DEFAULT_MODELS, verify_models, executable, run_spice, data, crossing, header

VDD = 1.8
# Published SKY130 values (see README.txt in this folder for sources)
CONTACT = {'licon': 15.0, 'mcon': 152.0, 'via': 4.5, 'via2': 3.41, 'via3': 3.41, 'via4': 0.38}  # ohm per cut, SkyWater RCX Table 91
WIRE = {  # ohm/um, fF/um for minimum-width wires, from the HD tech LEF (lesson 26 table)
    'met1': (0.125 / 0.14, 0.0847), 'met3': (0.047 / 0.30, 0.086)}
CIN_INV1 = 2.302  # fF, Liberty tt_025C_1v80 pin A

def wr(folder, vecs):
    return 'set wr_vecnames\nset wr_singlescale\nset numdgt=10\n'

def devices(engine, out):
    res = {}
    for name, model, w in (('nmos', 'sky130_fd_pr__nfet_01v8', 0.65), ('pmos', 'sky130_fd_pr__pfet_01v8_hvt', 1.0)):
        f = out / f'device_{name}'
        if name == 'nmos':
            inst = f'XM d g 0 0 {model} w={w} l=0.15\nVD d 0 1.8\nVG g 0 1.8\n'
        else:  # source and body at VDD; sweep the drain and gate voltages measured from ground
            inst = f'VS s 0 1.8\nXM d g s s {model} w={w} l=0.15\nVD d 0 0\nVG g 0 0\n'
        sweeps = ''
        for vg in (0.9, 1.2, 1.5, 1.8):
            gate = vg if name == 'nmos' else 1.8 - vg
            sweeps += f'alter VG dc={gate}\ndc VD 0 1.8 0.005\nwrdata ivd_{int(vg*10)}.dat i(VD)\n'
        dvd = 1.8 if name == 'nmos' else 0.0
        lvd = 0.05 if name == 'nmos' else 1.75
        deck = f'''* {name} {model} W={w} L=0.15 tt 25C
{header(DEFAULT_MODELS, f)}{inst}.control
{wr(f, None)}{sweeps}alter VD dc={dvd}
dc VG 0 1.8 0.005
wrdata ivg_sat.dat i(VD)
alter VD dc={lvd}
dc VG 0 1.8 0.005
wrdata ivg_lin.dat i(VD)
quit
.endc
.end
'''
        run_spice(engine, f, deck)
        fam = {}
        for vg in (0.9, 1.2, 1.5, 1.8):
            d = data(f / f'ivd_{int(vg*10)}.dat')
            vds = d[:, 0] if name == 'nmos' else 1.8 - d[:, 0]
            i = np.abs(d[:, 1])
            o = np.argsort(vds); fam[vg] = (vds[o], i[o])
        sat = data(f / 'ivg_sat.dat'); lin = data(f / 'ivg_lin.dat')
        vgs_s = sat[:, 0] if name == 'nmos' else 1.8 - sat[:, 0]
        vgs_l = lin[:, 0] if name == 'nmos' else 1.8 - lin[:, 0]
        o = np.argsort(vgs_s); vgs_s, isat = vgs_s[o], np.abs(sat[o, 1])
        o = np.argsort(vgs_l); vgs_l, ilin = vgs_l[o], np.abs(lin[o, 1])
        vds, i18 = fam[1.8]
        ion = float(np.interp(1.8, vds, i18)); i09 = float(np.interp(0.9, vds, i18))
        ioff = float(isat[0])
        # gm at Vgs=Vds=1.8 from the saturation transfer curve; gds from the output curve
        gm = float(np.gradient(isat, vgs_s)[-1])
        k = np.searchsorted(vds, 1.5); gds = float((i18[-1] - i18[k]) / (vds[-1] - vds[k]))
        # linear-extrapolated threshold at low Vds (max-gm method)
        g = np.gradient(ilin, vgs_l); j = int(np.argmax(g)); vt_lin = float(vgs_l[j] - ilin[j] / g[j] - lvd_abs(name) / 2)
        # alpha-power fit of Idsat(Vgs) at |Vds| = 1.8 for 1.0..1.8 V: I = K (Vgs - Vt)^alpha
        best = None
        for vt in np.arange(0.30, 0.80, 0.005):
            m = (vgs_s >= 1.0)
            x = np.log(vgs_s[m] - vt); y = np.log(isat[m])
            a, b = np.polyfit(x, y, 1); err = float(np.sum((y - (a * x + b)) ** 2))
            if best is None or err < best[0]: best = (err, float(vt), float(a), float(np.exp(b)))
        # effective switching resistance: average of Vds/Id over Vds from VDD down to VDD/2 at Vgs = VDD
        m = (vds >= 0.9)
        reff = float(np.trapezoid(vds[m] / i18[m], vds[m]) / (1.8 - 0.9))
        res[name] = dict(model=model, w_um=w, l_um=0.15, ion_uA=ion * 1e6, ion_uA_per_um=ion * 1e6 / w,
                         id_vgs18_vds09_uA=i09 * 1e6, ioff_pA=ioff * 1e12, gm_uS=gm * 1e6, gds_uS=gds * 1e6,
                         rout_kohm=1e-3 / gds, intrinsic_gain=gm / gds, vt_lin_extrap_V=vt_lin,
                         alpha_fit=dict(vt_V=best[1], alpha=best[2], K=best[3]),
                         reff_avg_kohm=reff / 1e3, vdd_over_ion_kohm=1.8 / ion / 1e3,
                         ron_linear_kohm=lvd_abs(name) / float(np.interp(1.8, vgs_l, ilin)) / 1e3,
                         curves={str(vg): dict(vds=fam[vg][0][::4].round(4).tolist(), id_uA=(fam[vg][1][::4] * 1e6).round(3).tolist()) for vg in fam},
                         transfer=dict(vgs=vgs_s[::4].round(4).tolist(), id_A=isat[::4].tolist()))
    return res

def lvd_abs(name):
    return 0.05

def tran_deck(f, body, tstop='6n', step='0.5p', saves='', corner='tt', temp=25):
    return f'''* delay physics
{header(DEFAULT_MODELS, f, corner, temp)}{body}
.control
set wr_vecnames
set wr_singlescale
set numdgt=10
tran {step} {tstop} 0 {step}
wrdata tran.dat {saves}
quit
.endc
.end
'''

SRC = lambda vdd=1.8: f'VDD vdd 0 {vdd}\nVIN in 0 PULSE(0 {vdd} 0.3n 20p 20p 2n 4n)\nXS0 in 0 0 vdd vdd s0 inv1\nXS1 s0 0 0 vdd vdd a inv1\n'
# two shaping inverters give the device under test a realistic input edge

def delays(t, vin, vout, vdd, after=0.2e-9):
    """input rising at a: output falls -> tphl; input falling: tplh. a is non-inverted copy of in."""
    r = crossing(t, vin, vdd / 2, True, after); fo = crossing(t, vout, vdd / 2, False, r - 1e-12)
    fl = crossing(t, vin, vdd / 2, False, r + 0.1e-9); ro = crossing(t, vout, vdd / 2, True, fl - 1e-12)
    return (fo - r) * 1e12, (ro - fl) * 1e12, r, fl

def slew(t, v, vdd, rising, after):
    lo, hi = 0.2 * vdd, 0.8 * vdd
    if rising: return (crossing(t, v, hi, True, after) - crossing(t, v, lo, True, after)) * 1e12
    return (crossing(t, v, lo, False, after) - crossing(t, v, hi, False, after)) * 1e12

def fanout(engine, out):
    res = {'fanout': [], 'waves': {}}
    for n in (1, 2, 4, 8, 16):
        f = out / f'fanout_{n}'
        body = SRC() + 'XDUT a 0 0 vdd vdd y inv1\n'
        for k in range(n):
            body += f'XL{k} y 0 0 vdd vdd z{k} inv1\nCZ{k} z{k} 0 9.208f\n'
        run_spice(engine, f, tran_deck(f, body, saves='v(a) v(y)'))
        d = data(f / 'tran.dat'); t, va, vy = d.T
        tphl, tplh, r, fl = delays(t, va, vy, VDD)
        row = dict(n=n, tphl_ps=tphl, tplh_ps=tplh, avg_ps=(tphl + tplh) / 2,
                   fall_slew_ps=slew(t, vy, VDD, False, r), rise_slew_ps=slew(t, vy, VDD, True, fl),
                   in_rise_slew_ps=slew(t, va, VDD, True, 0.2e-9), in_fall_slew_ps=slew(t, va, VDD, False, r + 0.1e-9),
                   liberty_load_fF=n * CIN_INV1)
        res['fanout'].append(row)
        m = (t >= r - 0.05e-9) & (t <= r + 0.6e-9)
        res['waves'][str(n)] = dict(t_ps=((t[m] - r) * 1e12)[::4].round(2).tolist(), y=vy[m][::4].round(4).tolist())
        if n == 1:
            res['waves']['in'] = dict(t_ps=((t[m] - r) * 1e12)[::4].round(2).tolist(), y=va[m][::4].round(4).tolist())
    return res

def fo4(engine, out, size=1, vdd=1.8, tag='', half=2.0):
    """Chain of 5 inv_size stages, each driving the next stage plus 3 identical dummy inverters (fanout 4).
    Each dummy drives its own fanout-of-4 capacitor so its Miller loading is realistic. Measure stage 3.
    DUT stage gets its own supply source so its energy can be measured."""
    f = out / f'fo4_inv{size}_{vdd:.1f}V{tag}'
    cl = 4 * CIN_INV1 * size
    body = f'VDD vdd 0 {vdd}\nVDUT vdut 0 {vdd}\nVIN in 0 PULSE(0 {vdd} 0.3n 20p 20p {half}n {2*half}n)\nXS0 in 0 0 vdd vdd s0 inv{size}\nXS1 s0 0 0 vdd vdd n0 inv{size}\n'
    for s in range(1, 6):
        sup = 'vdut' if s == 3 else 'vdd'
        body += f'X{s} n{s-1} 0 0 {sup} {sup} n{s} inv{size}\n'
        for k in range(3):
            body += f'XD{s}_{k} n{s} 0 0 vdd vdd d{s}_{k} inv{size}\nCD{s}_{k} d{s}_{k} 0 {cl}f\n'
    body += f'CEND n5 0 {cl}f\n'
    deck = tran_deck(f, body, tstop=f'{2*half+0.3}n', saves='v(n2) v(n3) i(VDUT)')
    run_spice(engine, f, deck)
    d = data(f / 'tran.dat'); t, v2, v3, i = d.T
    # stage 3 input n2 rises for the first input rising edge? n0 = in after 2 inversions -> n2 follows in
    r = crossing(t, v2, vdd / 2, True, 0.2e-9); fo_ = crossing(t, v3, vdd / 2, False, r - 1e-12)
    fl = crossing(t, v2, vdd / 2, False, r + 0.1e-9); ro = crossing(t, v3, vdd / 2, True, fl - 1e-12)
    tphl, tplh = (fo_ - r) * 1e12, (ro - fl) * 1e12
    # energy from the DUT supply over one full period starting before the first edge
    t0, t1 = 0.25e-9, (2 * half + 0.25) * 1e-9; m = (t >= t0) & (t <= t1)
    e = float(np.trapezoid(-vdd * i[m], t[m])) * 1e15
    return dict(size=size, vdd=vdd, tphl_ps=tphl, tplh_ps=tplh, fo4_ps=(tphl + tplh) / 2,
                energy_per_cycle_fJ=e, load_cap_external_fF=4 * CIN_INV1 * size)

def leakage(engine, out, vdd):
    f = out / f'leak_{vdd:.1f}V'
    body = f'VDD vdd 0 {vdd}\nVA0 a0 0 0\nVA1 a1 0 {vdd}\nVD0 vd0 0 {vdd}\nVD1 vd1 0 {vdd}\nX0 a0 0 0 vd0 vd0 y0 inv1\nX1 a1 0 0 vd1 vd1 y1 inv1\n'
    deck = f'''* leakage
{header(DEFAULT_MODELS, f)}{body}
.control
op
print i(VD0) i(VD1)
quit
.endc
.end
'''
    log = run_spice(engine, f, deck)
    vals = {}
    for line in log.splitlines():
        s = line.strip().lower()
        if s.startswith('i(vd0)') or s.startswith('i(vd1)'):
            k, v = s.split('=')
            vals[k.strip()] = abs(float(v))
    return dict(vdd=vdd, in_low_nA=vals['i(vd0)'] * 1e9, in_high_nA=vals['i(vd1)'] * 1e9,
                avg_power_pW=vdd * (vals['i(vd0)'] + vals['i(vd1)']) / 2 * 1e12)

def wire_chain(engine, out, layer, length, drv=1, nseg=20):
    """driver inv_drv -> cuts up -> uniform wire (nseg pi-sections) -> cuts down -> inv_1 load (+ its FO4 cap)."""
    r_um, c_um = WIRE[layer]
    rw, cw = r_um * length, c_um * length
    if layer == 'met1':
        up = CONTACT['mcon']; down = CONTACT['mcon']
    else:  # li1 pin -> mcon -> met1 -> via -> met2 -> via2 -> met3
        up = CONTACT['mcon'] + CONTACT['via'] + CONTACT['via2']; down = up
    f = out / f'wire_{layer}_{int(length)}um_inv{drv}'
    body = SRC() + f'XDRV a 0 0 vdd vdd y inv{drv}\nRUP y w0 {up}\n'
    for k in range(nseg):
        body += f'CW{k}a w{k} 0 {cw/nseg/2}f\nRW{k} w{k} w{k+1} {rw/nseg}\nCW{k}b w{k+1} 0 {cw/nseg/2}f\n'
    body += f'RDN w{nseg} g {down}\nXLD g 0 0 vdd vdd z inv1\nCZ z 0 9.208f\n'
    run_spice(engine, f, tran_deck(f, body, tstop='8n' if rw * cw > 5e5 else '6n', saves='v(a) v(y) v(g)').replace('PULSE(0 1.8 0.3n 20p 20p 2n 4n)', 'PULSE(0 1.8 0.3n 20p 20p 3n 6n)'))
    d = data(f / 'tran.dat'); t, va, vy, vg = d.T
    near_hl, near_lh, r, fl = delays(t, va, vy, VDD)
    far_hl, far_lh, _, _ = delays(t, va, vg, VDD)
    return dict(layer=layer, length_um=length, driver=f'inv{drv}', r_wire_ohm=rw, c_wire_fF=cw, r_cuts_up_ohm=up, r_cuts_down_ohm=down,
                near_tphl_ps=near_hl, near_tplh_ps=near_lh, far_tphl_ps=far_hl, far_tplh_ps=far_lh,
                far_avg_ps=(far_hl + far_lh) / 2, far_fall_slew_ps=slew(t, vg, VDD, False, r), far_rise_slew_ps=slew(t, vg, VDD, True, fl))

def repeaters(engine, out, length=3000, layer='met1', size=4, nseg_total=60):
    r_um, c_um = WIRE[layer]
    res = []
    for k in (1, 2, 3, 4, 6, 8):
        f = out / f'rep_{layer}_{length}um_{k}seg_inv{size}'
        seg = length / k; rw, cw = r_um * seg, c_um * seg; ns = max(4, nseg_total // k)
        body = SRC().replace('XS1 s0 0 0 vdd vdd a inv1', f'XS1 s0 0 0 vdd vdd a inv{max(1, size // 4)}') + f'XDRV0 a 0 0 vdd vdd y0_0 inv{size}\n'
        for j in range(k):
            body += f'RUP{j} y{j}_0 w{j}_0 {CONTACT["mcon"]}\n'
            for s in range(ns):
                body += f'CA{j}_{s} w{j}_{s} 0 {cw/ns/2}f\nRW{j}_{s} w{j}_{s} w{j}_{s+1} {rw/ns}\nCB{j}_{s} w{j}_{s+1} 0 {cw/ns/2}f\n'
            nxt = f'g{j}'
            body += f'RDN{j} w{j}_{ns} {nxt} {CONTACT["mcon"]}\n'
            if j < k - 1:
                body += f'XR{j} {nxt} 0 0 vdd vdd y{j+1}_0 inv{size}\n'
        body += f'XLD g{k-1} 0 0 vdd vdd z inv1\nCZ z 0 9.208f\n'
        run_spice(engine, f, tran_deck(f, body, tstop='16n', saves=f'v(a) v(g{k-1})').replace('PULSE(0 1.8 0.3n 20p 20p 2n 4n)', 'PULSE(0 1.8 0.3n 20p 20p 7n 14n)'))
        d = data(f / 'tran.dat'); t, va, vg = d.T
        r = crossing(t, va, VDD / 2, True, 0.2e-9); fl = crossing(t, va, VDD / 2, False, r + 0.1e-9)
        rising_out = (k % 2 == 0)  # k inverters total
        o1 = crossing(t, vg, VDD / 2, rising_out, r - 1e-12); o2 = crossing(t, vg, VDD / 2, not rising_out, fl - 1e-12)
        res.append(dict(segments=k, repeaters=k - 1, driver=f'inv{size}', delay_edge1_ps=(o1 - r) * 1e12, delay_edge2_ps=(o2 - fl) * 1e12,
                        avg_ps=((o1 - r) + (o2 - fl)) / 2 * 1e12))
    return dict(layer=layer, length_um=length, size=size, r_wire_ohm=r_um*length, c_wire_fF=c_um*length, results=res)

def sizing(engine, out, cl=50.0):
    res = []
    for size in (1, 2, 4, 8):
        f = out / f'size_inv{size}_{int(cl)}fF'
        body = SRC().replace('XS1 s0 0 0 vdd vdd a inv1', 'XS1 s0 0 0 vdd vdd a inv4') + f'VDUT vdut 0 1.8\nXDUT a 0 0 vdut vdut y inv{size}\nCL y 0 {cl}f\n'
        run_spice(engine, f, tran_deck(f, body, tstop='4.3n', saves='v(a) v(y) i(VDUT)'))
        d = data(f / 'tran.dat'); t, va, vy, i = d.T
        tphl, tplh, r, fl = delays(t, va, vy, VDD)
        m = (t >= 0.25e-9) & (t <= 4.25e-9); e = float(np.trapezoid(-1.8 * i[m], t[m])) * 1e15
        res.append(dict(size=size, tphl_ps=tphl, tplh_ps=tplh, avg_ps=(tphl + tplh) / 2, energy_per_cycle_fJ=e,
                        cl_fF=cl, cv2_fJ=cl * 1.8 ** 2))
    return res

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--ngspice'); ap.add_argument('--output', type=Path, default=HERE / 'run_results')
    ap.add_argument('--only', help='run one experiment group and merge it into an existing summary.json')
    a = ap.parse_args(); eng = executable(a.ngspice, 'NGSPICE_BIN', 'ngspice'); verify_models()
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    if a.only == 'repeaters':
        R = json.loads((out / 'summary.json').read_text())
        R['repeaters'] = [repeaters(eng, out, L, 'met1', s) for L in (3000, 6000) for s in (4, 16)]
        (out / 'summary.json').write_text(json.dumps(R, indent=1)); return
    R = {'scope': 'ngspice transient/DC runs of the bundled SKY130 tt models at 25 C. Inverters are the inv_1 device pair in parallel; no cell layout parasitics. Wire values from the HD tech LEF; cut resistances from SkyWater RCX Table 91. Teaching estimates, not signoff.'}
    R['devices'] = devices(eng, out)
    R.update(fanout(eng, out))
    R['fo4'] = [fo4(eng, out, s) for s in (1, 4)]
    R['vdd_sweep'] = [fo4(eng, out, 1, v, half=(20.0 if v < 1.15 else 2.0)) for v in (1.0, 1.2, 1.4, 1.6, 1.8)]
    R['leakage'] = [leakage(eng, out, v) for v in (1.0, 1.2, 1.4, 1.6, 1.8)]
    R['sizing_50fF'] = sizing(eng, out)
    R['wires'] = [wire_chain(eng, out, lay, L, drv) for lay in ('met1', 'met3') for L in (10, 100, 300, 1000, 2000) for drv in (1, 4)]
    R['repeaters'] = [repeaters(eng, out, L, 'met1', s) for L in (3000, 6000) for s in (4, 16)]
    (out / 'summary.json').write_text(json.dumps(R, indent=1))
    print('wrote', out / 'summary.json')

if __name__ == '__main__':
    main()
