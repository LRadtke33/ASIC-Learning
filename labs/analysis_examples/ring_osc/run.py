#!/usr/bin/env python3
"""11-stage inv_1 ring vs VDD. stdlib only. Writes ring_osc.json next to this file."""
from pathlib import Path
import subprocess, os, math, json, time, hashlib

HERE = Path(__file__).resolve().parent
MODELS = HERE.parents[1] / 'common' / 'models' / 'sky130_course.lib.spice'
N = 11
VDDS = [1.00, 1.20, 1.40, 1.60, 1.80, 1.95]
TSTOPS = {1.00: 80e-9, 1.20: 40e-9, 1.40: 30e-9, 1.60: 20e-9, 1.80: 20e-9, 1.95: 20e-9}
TSTEP  = {1.00: 5e-12, 1.20: 2e-12, 1.40: 1e-12, 1.60: 1e-12, 1.80: 1e-12, 1.95: 1e-12}

def deck(folder, vdd, tstop, tstep):
    lib = os.path.relpath(MODELS, folder)
    insts = '\n'.join(f'X{i} n{i} VGND VGND VPWR VPWR n{i%N+1} inv1' for i in range(1, N+1))
    return f'''* 11-stage inv_1 ring, tt 25C, VDD={vdd}
.lib "{lib}" tt
.temp 25
.options reltol=1e-5 abstol=1e-14 vntol=1e-8
.subckt inv1 A VGND VNB VPB VPWR Y
XN0 Y A VGND VNB sky130_fd_pr__nfet_01v8 w=0.65 l=0.15
XP0 Y A VPWR VPB sky130_fd_pr__pfet_01v8_hvt w=1.0 l=0.15
.ends
VDD VPWR 0 {vdd}
VSS VGND 0 0
{insts}
.ic v(n1)=0
.tran {tstep} {tstop} 0 {tstep}
.control
unset askquit
run
wrdata n1.csv v(n1)
echo DONE
.endc
.end
'''

def parse_wrdata(path):
    ts, ys = [], []
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                ts.append(float(parts[0])); ys.append(float(parts[1]))
            except ValueError:
                continue
    return ts, ys

def crossings(t, y, level, after=0.0):
    out = []
    for i in range(len(t)-1):
        if t[i] < after:
            continue
        a, b = y[i], y[i+1]
        if a < level <= b and b != a:
            out.append(t[i] + (level-a)*(t[i+1]-t[i])/(b-a))
    return out

def main():
    ver = subprocess.run(['ngspice', '--version'], capture_output=True, text=True).stdout
    results = []
    for vdd in VDDS:
        folder = HERE / 'decks' / f'v{vdd:.2f}'
        folder.mkdir(parents=True, exist_ok=True)
        (folder/'bench.spice').write_text(deck(folder, vdd, TSTOPS[vdd], TSTEP[vdd]))
        env = os.environ.copy(); env['OMP_NUM_THREADS'] = '1'
        t0 = time.time()
        p = subprocess.run(['ngspice', '-b', 'bench.spice'], cwd=folder,
                           capture_output=True, text=True, timeout=180, env=env)
        log = p.stdout + '\n' + p.stderr
        (folder/'ngspice.log').write_text(log)
        if p.returncode or 'fatal' in log.lower() or 'error:' in log.lower():
            raise SystemExit(f'ngspice failed at {vdd} V:\n{log[-2000:]}')
        ts, ys = parse_wrdata(folder/'n1.csv')
        rises = crossings(ts, ys, vdd/2, after=(ts[-1]*0.25 if ts else 0))
        periods = [rises[i+1]-rises[i] for i in range(len(rises)-1)]
        if not periods:
            raise SystemExit(f'no periods at {vdd} V')
        T = sum(periods)/len(periods)
        rec = {
            'vdd': vdd, 'tstop_s': TSTOPS[vdd], 'tstep_s': TSTEP[vdd],
            'n_samples': len(ts), 'n_periods': len(periods),
            'period_s': T, 'freq_Hz': 1/T, 'td_avg_s': T/(2*N),
            'period_ps': T*1e12, 'freq_MHz': 1e-6/T, 'td_ps': T/(2*N)*1e12,
            'seconds': time.time()-t0,
        }
        results.append(rec)
        print(vdd, 'f_MHz', round(rec['freq_MHz'], 2), 'td_ps', round(rec['td_ps'], 2))
    out = {
        'tool': ver.strip().splitlines()[1] if 'ngspice-' in ver else ver.strip(),
        'conditions': 'tt 25 C, course models, 11-stage inv_1 device-pair ring, schematic only',
        'formula': 'f = 1/(2 N t_d), N=11, t_d = T/(2N) from VDD/2 rising crossings after the first quarter of the transient',
        'model_wrapper_sha256': hashlib.sha256(MODELS.read_bytes()).hexdigest(),
        'results': results,
    }
    (HERE/'ring_osc.json').write_text(json.dumps(out, indent=2))
    print('wrote', HERE/'ring_osc.json')

if __name__ == '__main__':
    main()
