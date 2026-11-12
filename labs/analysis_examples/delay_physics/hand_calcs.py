#!/usr/bin/env python3
"""Hand calculations quoted in lessons 27 and 34, recomputed from the recorded results.
Run from learning/: python labs/analysis_examples/delay_physics/hand_calcs.py
Reads results/spice_summary.json, results/liberty_summary.json, results/device_params.json; writes results/hand_calcs.json."""
from pathlib import Path
import json, math
import numpy as np
H = Path(__file__).resolve().parent / 'results'
S = json.loads((H / 'spice_summary.json').read_text()); L = json.loads((H / 'liberty_summary.json').read_text())
P = json.loads((H / 'device_params.json').read_text())
E0 = 8.854e-12; VDD = 1.8; C = {}
# A. oxide and gate capacitance
n, p = P['nfet_01v8'], P['pfet_01v8_hvt']
cox_n = 3.9 * E0 / n['toxe_m'] * 1e3  # fF/um^2  (F/m^2 * 1e15 fF/F * 1e-12 m^2/um^2 = *1e3)
cox_p = 3.9 * E0 / p['toxe_m'] * 1e3
cov_n = n['cgso_F_per_m'] * 1e9  # fF/um  (F/m *1e15 *1e-6)
cov_p = p['cgso_F_per_m'] * 1e9
cg_ch = cox_n * 0.65 * 0.15 + cox_p * 1.0 * 0.15
cg_ov = 2 * (cov_n * 0.65 + cov_p * 1.0)
C['gate_cap'] = dict(cox_n_fF_um2=cox_n, cox_p_fF_um2=cox_p, cov_n_fF_um=cov_n, cov_p_fF_um=cov_p,
                     channel_n_fF=cox_n * 0.0975, channel_p_fF=cox_p * 0.15, channel_fF=cg_ch, overlap_fF=cg_ov,
                     total_fF=cg_ch + cg_ov, liberty_fF=2.302)
# B. effective resistance
D = S['devices']; R = {}
for k in ('nmos', 'pmos'):
    d = D[k]; R[k] = dict(ion_uA=d['ion_uA'], three_quarter_vdd_over_ion_kohm=0.75 * VDD / d['ion_uA'] * 1e3,
                         integral_kohm=d['reff_avg_kohm'], deep_triode_kohm=d['ron_linear_kohm'],
                         lambda_per_V=d['gds_uS'] / d['ion_uA'], rout_kohm=d['rout_kohm'], gm_uS=d['gm_uS'], gm_rout=d['intrinsic_gain'],
                         gm_over_id_per_V=d['gm_uS'] / d['ion_uA'])
R['liberty_inv_1'] = dict(fall_kohm=L['reff_fits']['inv_1']['fall']['reff_kohm'], rise_kohm=L['reff_fits']['inv_1']['rise']['reff_kohm'])
C['reff'] = R
# C. square law vs measured transfer: anchor at Vgs=1.0 and extrapolate to 1.8
for k in ('nmos', 'pmos'):
    tr = D[k]['transfer']; vg = np.array(tr['vgs']); i = np.array(tr['id_A'])
    vt = D[k]['alpha_fit']['vt_V']; i10 = float(np.interp(1.0, vg, i)); i18 = float(np.interp(1.8, vg, i))
    C.setdefault('square_law', {})[k] = dict(vt_fit_V=vt, alpha=D[k]['alpha_fit']['alpha'], i_1p0_uA=i10 * 1e6, i_1p8_uA=i18 * 1e6,
        square_law_prediction_uA=i10 * ((1.8 - vt) / (1.0 - vt)) ** 2 * 1e6, linear_prediction_uA=i10 * ((1.8 - vt) / (1.0 - vt)) * 1e6)
# E. FO4 estimate from device numbers and Liberty self-cap fits
cin = 2.302; lf = L['reff_fits']['inv_1']
fo4 = {}
for edge, dev in (('fall', 'nmos'), ('rise', 'pmos')):
    cs = lf[edge]['c_self_fF']
    fo4[edge] = dict(r_iv_kohm=D[dev]['reff_avg_kohm'], c_self_fF=cs, c_load_fF=4 * cin,
                     est_ps=0.69 * D[dev]['reff_avg_kohm'] * (cs + 4 * cin))
fo4['sim_tphl_ps'] = S['fanout'][2]['tphl_ps']; fo4['sim_tplh_ps'] = S['fanout'][2]['tplh_ps']
fo4['sim_fo4_chain_ps'] = S['fo4'][0]['fo4_ps']
lib4 = [r for r in L['fanout_liberty'] if r['n'] == 4][0]; fo4['liberty_rise_ps'] = lib4['rise_ps']; fo4['liberty_fall_ps'] = lib4['fall_ps']
fo4['liberty_avg_ps'] = (lib4['rise_ps'] + lib4['fall_ps']) / 2
fo4['tau_ps'] = fo4['sim_fo4_chain_ps'] / 5
C['fo4'] = fo4
# F. via stacks
T91 = dict(licon=15.0, mcon=152.0, via=4.5, via2=3.41, via3=3.41, via4=0.38)
ORFS = dict(mcon=9.249146, via=4.5, via2=3.368786, via3=0.376635, via4=0.0058)
def stack(tab, top):
    order = ['mcon', 'via', 'via2', 'via3', 'via4']; seq = order[:order.index(top) + 1]
    return sum(tab[x] for x in seq)
C['via_stacks'] = {f'li1_to_{m}': dict(table91_1cut=stack(T91, v), table91_2cut=stack(T91, v) / 2, orfs_1cut=stack(ORFS, v), orfs_2cut=stack(ORFS, v) / 2)
                   for m, v in (('met1', 'mcon'), ('met2', 'via'), ('met3', 'via2'), ('met4', 'via3'), ('met5', 'via4'))}
# G. wires: sheet, width, thickness from lesson 26 table (HD tech LEF)
LAY = dict(li1=(12.2, 0.17, 0.10, 0.088), met1=(0.125, 0.14, 0.35, 0.085), met2=(0.125, 0.14, 0.35, 0.078),
           met3=(0.047, 0.30, 0.80, 0.086), met4=(0.047, 0.30, 0.80, 0.076), met5=(0.0285, 1.60, 1.20, 0.088))
C['wires'] = {k: dict(rs=v[0], w_um=v[1], t_um=v[2], r_per_um=v[0] / v[1], c_fF_per_um=v[3], implied_rho_uohm_cm=v[0] * v[2] * 100,
                      rc_1mm_ps=(v[0] / v[1] * 1000) * (v[3] * 1000) * 1e-3, rc_half_1mm_ps=0.5 * (v[0] / v[1] * 1000) * (v[3] * 1000) * 1e-3)
              for k, v in LAY.items()}
# H. Elmore of an N-section ladder, normalized to total RC
C['ladder'] = {str(N): (N + 1) / (2 * N) for N in (1, 2, 3, 5, 10, 100)}
# I. worked chain: inv_4 -> li1 pin -> mcon/via/via2 -> 1000 um met3 -> back down -> inv_1 gate
def chain(drv, layer, Lum, cuts_up, cuts_dn, cl=2.302):
    rw = LAY[layer][0] / LAY[layer][1] * Lum; cw = (0.086 if layer == 'met3' else 0.0847) * Lum
    out = dict(r_wire=rw, c_wire=cw, r_up=cuts_up, r_dn=cuts_dn, c_load=cl)
    for edge in ('fall', 'rise'):
        rd = L['reff_fits'][drv][edge]['reff_kohm'] * 1e3; cs = L['reff_fits'][drv][edge]['c_self_fF']
        terms = dict(driver_ps=0.69 * rd * (cs + cw + cl) * 1e-3, cuts_up_ps=0.69 * cuts_up * (cw + cl) * 1e-3,
                     wire_distributed_ps=0.38 * rw * cw * 1e-3, wire_into_load_ps=0.69 * rw * cl * 1e-3, cuts_down_ps=0.69 * cuts_dn * cl * 1e-3)
        elm = (rd * (cs + cw + cl) + cuts_up * (cw + cl) + rw * (cw / 2 + cl) + cuts_dn * cl) * 1e-3
        out[edge] = dict(rd_ohm=rd, c_self_fF=cs, terms=terms, t50_est_ps=sum(terms.values()), elmore_ps=elm)
    return out
up3 = T91['mcon'] + T91['via'] + T91['via2']
ex = chain('inv_4', 'met3', 1000, up3, up3)
sim = [w for w in S['wires'] if w['layer'] == 'met3' and w['length_um'] == 1000 and w['driver'] == 'inv4'][0]
ex['sim_far_tphl_ps'] = sim['far_tphl_ps']; ex['sim_far_tplh_ps'] = sim['far_tplh_ps']; ex['sim_near_tphl_ps'] = sim['near_tphl_ps']; ex['sim_near_tplh_ps'] = sim['near_tplh_ps']
C['worked_chain'] = ex
C['worked_chain_orfs_cuts'] = chain('inv_4', 'met3', 1000, stack(ORFS, 'via2'), stack(ORFS, 'via2'))
# J. scaling table
C['scaling'] = []
for w in S['wires']:
    up = T91['mcon'] if w['layer'] == 'met1' else up3
    e = chain(w['driver'].replace('inv', 'inv_'), w['layer'], w['length_um'], up, up)
    C['scaling'].append(dict(layer=w['layer'], L=w['length_um'], driver=w['driver'], est_avg_ps=(e['fall']['t50_est_ps'] + e['rise']['t50_est_ps']) / 2,
                             sim_avg_ps=w['far_avg_ps'], wire_part_ps=(e['fall']['terms']['wire_distributed_ps'])))
# K. repeaters (Bakoglu) for 6 mm minimum met1 using inv_1 as the unit
r0 = (lf['rise']['reff_kohm'] + lf['fall']['reff_kohm']) / 2 * 1e3; c0 = cin
rw = 0.125 / 0.14 * 6000; cw = 0.0847 * 6000
C['repeaters_bakoglu'] = dict(r0_ohm=r0, c0_fF=c0, rw_ohm=rw, cw_fF=cw, k_opt=math.sqrt(0.4 * rw * cw / (0.7 * r0 * c0)),
                              h_opt=math.sqrt(r0 * cw / (rw * c0)), unbuffered_wire_term_ps=0.38 * rw * cw * 1e-3,
                              sim={str(rr['length_um']) + '_inv' + str(rr['size']): [(x['segments'], x['avg_ps']) for x in rr['results']] for rr in S['repeaters']})
# critical length where 0.38 r c L^2 equals the FO4 delay, minimum met1 and met3
for lay, cpu in (('met1', 0.0847), ('met3', 0.086)):
    r = LAY[lay][0] / LAY[lay][1]
    C.setdefault('crit_length_um', {})[lay] = math.sqrt(fo4['sim_fo4_chain_ps'] * 1e3 / (0.38 * r * cpu))
# L. fanout fit
ns = np.array([r['n'] for r in S['fanout']]); av = np.array([r['avg_ps'] for r in S['fanout']])
sl, ic = np.polyfit(ns, av, 1); C['fanout_fit'] = dict(slope_ps_per_load=sl, intercept_ps=ic, sim=[(int(a), float(b)) for a, b in zip(ns, av)])
# M. buffer tree for 64 inv_1 loads, Liberty, with slew propagation; average of both output edges at the loads
import importlib.util, sys
spec = importlib.util.spec_from_file_location('lp', str(H.parent / 'liberty_path.py')); lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
def tree(stages, final_load_pf, start_slew=0.05):
    # stages: list of (cell, fanout of that stage in copies of next cell or None for the final)
    res = []
    for first in ('rise', 'fall'):
        edge = first; slew = start_slew; tot = 0.0
        for i, (c, load) in enumerate(stages):
            d, s = lp.stage(c, 'Y', 'A', slew, load, edge); tot += d; slew = s; edge = 'fall' if edge == 'rise' else 'rise'
        res.append(tot)
    return sum(res) / 2 * 1e3
cin_pf = 2.302e-3; c = {x: lp.cap(x, 'A') for x in ('inv_1', 'inv_2', 'inv_4', 'inv_8')}
C['buffer_tree_64'] = {
    'inv_1 drives 64 loads directly': tree([('inv_1', 64 * cin_pf)], None),
    'inv_1 -> inv_8 -> 64 loads (2 stages)': tree([('inv_1', c['inv_8']), ('inv_8', 64 * cin_pf)], None),
    'inv_1 -> inv_4 -> 4 x inv_4 -> 16 loads each (3 stages, fanout 4 each)': tree([('inv_1', c['inv_4']), ('inv_4', 4 * c['inv_4']), ('inv_4', 16 * cin_pf)], None),
    'inv_1 -> inv_2 -> 2 x inv_8 -> 32 loads each (3 stages)': tree([('inv_1', c['inv_2']), ('inv_2', 2 * c['inv_8']), ('inv_8', 32 * cin_pf)], None),
}
C['buffer_tree_note'] = 'Liberty tt_025C_1v80, input slew 0.05 ns, no wire; average of the two output edges; inverting trees flip polarity (ignored here).'
# N. power
vs = S['vdd_sweep']
C['vdd_sweep'] = [dict(vdd=r['vdd'], fo4_ps=r['fo4_ps'], energy_fJ=r['energy_per_cycle_fJ'], e_over_v2_fF=r['energy_per_cycle_fJ'] / r['vdd'] ** 2,
                       edp_fJ_ns=r['energy_per_cycle_fJ'] * r['fo4_ps'] * 1e-3, leak_pW=[x for x in S['leakage'] if abs(x['vdd'] - r['vdd']) < 1e-6][0]['avg_power_pW'])
                  for r in vs]
e18 = S['fo4'][0]['energy_per_cycle_fJ']
C['power_example'] = dict(e_cycle_fJ=e18, alpha=0.1, f_MHz=100, p_dyn_uW=0.1 * e18 * 1e-15 * 100e6 * 1e6, p_leak_pW_liberty=0.005326682 * 1e3,
                          ratio=0.1 * e18 * 1e-15 * 100e6 / (0.005326682e-9))
C['sizing_50fF'] = S['sizing_50fF']
for r, x in zip(C['sizing_50fF'], ('inv_1', 'inv_2', 'inv_4', 'inv_8')):
    r['cin_fF'] = lp.cap(x, 'A') * 1e3; r['input_energy_fJ'] = r['cin_fF'] * VDD ** 2; r['edp'] = r['energy_per_cycle_fJ'] * r['avg_ps'] * 1e-3
(H / 'hand_calcs.json').write_text(json.dumps(C, indent=1))

# O. exact step-input discharge time from the device curve: t50 = C * integral_{VDD/2}^{VDD} dV / I(V)
for k, edge in (('nmos', 'fall'), ('pmos', 'rise')):
    cv = D[k]['curves']['1.8']; v = np.array(cv['vds']); i = np.array(cv['id_uA']) * 1e-6
    m = v >= 0.9; integ = float(np.trapezoid(1 / i[m], v[m]))
    ctot = lf[edge]['c_self_fF'] + 4 * cin
    C.setdefault('step_integral', {})[k] = dict(integral_V_per_A=integ, c_total_fF=ctot, t50_ps=ctot * 1e-15 * integ * 1e12,
                                              const_current_t50_ps=ctot * 1e-15 * 0.9 / (D[k]['ion_uA'] * 1e-6) * 1e12)
# P. distributed RC step response: t50 and t63 of a 400-section ladder driven by an ideal step, no load
N = 400; Rs = 1.0 / N; Cs = 1.0 / N
A = np.zeros((N, N))
for j in range(N):
    A[j, j] = -2.0 / (Rs * Cs) if j < N - 1 else -1.0 / (Rs * Cs)
    if j > 0: A[j, j - 1] = 1.0 / (Rs * Cs)
    if j < N - 1: A[j, j + 1] = 1.0 / (Rs * Cs)
b = np.zeros(N); b[0] = 1.0 / (Rs * Cs)
w, V = np.linalg.eig(A); Vi = np.linalg.inv(V); x_inf = -np.linalg.solve(A, b)
ts = np.linspace(0, 2.0, 4001)
far = np.array([x_inf[-1] - (V @ (np.exp(w * t) * (Vi @ x_inf)))[-1].real for t in ts])
lum = 1 - np.exp(-ts)
C['distributed_step'] = dict(t50_over_RC=float(np.interp(0.5, far, ts)), t90_over_RC=float(np.interp(0.9, far, ts)),
                             lumped_t50_over_RC=float(np.log(2)), lumped_t90_over_RC=float(np.log(10)),
                             elmore_over_RC=0.5, curve_t=ts[::50].round(3).tolist(), curve_far=far[::50].round(4).tolist(), curve_lumped=lum[::50].round(4).tolist())
# Q. per-load fanout increment from device Reff
C['fanout_increment_est_ps'] = 0.69 * (D['nmos']['reff_avg_kohm'] + D['pmos']['reff_avg_kohm']) / 2 * cin
# R. Bakoglu with self-loading
cp = (lf['rise']['c_self_fF'] + lf['fall']['c_self_fF']) / 2
C['repeaters_bakoglu']['c_self_fF'] = cp
C['repeaters_bakoglu']['k_opt_with_self_load'] = math.sqrt(0.38 * rw * cw / (0.69 * r0 * (c0 + cp)))
(H / 'hand_calcs.json').write_text(json.dumps(C, indent=1))
