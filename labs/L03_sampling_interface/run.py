#!/usr/bin/env python3
"""Compare ideal, NMOS and transmission-gate acquisition, then a reference-load model."""
from pathlib import Path
import argparse,csv,json,sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'common'))
from lab_support import DEFAULT_MODELS,verify_models,executable,run_spice,data,relative_spice,metadata,plot_style

def write_csv(path,rows):
    with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ngspice');ap.add_argument('--models',type=Path,default=DEFAULT_MODELS);ap.add_argument('--output',type=Path,default=HERE/'run_results');args=ap.parse_args()
    engine=executable(args.ngspice,'NGSPICE_BIN','ngspice');verify_models();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    rows=[];waves={};cap=2e-12;lsb=1.8/4096
    cases=[(kind,rs,vin,acq) for kind in ['ideal','nmos','tg'] for rs in [1000,10000] for vin in [.1,.9,1.5] for acq in [5,20,80]]
    cases += [('tg_x8',1000,.9,acq) for acq in [20,80,200]]
    for kind,rs,vin,acq in cases:
        name=f'{kind}_R{rs}_Vin{vin:g}_acq{acq}ns';folder=out/name;off=10+acq;end=off+8
        switch='S1 src hold clk 0 SWTEACH\n.model SWTEACH SW(Ron=5 Roff=1e12 Vt=0.9 Vh=0.05)'
        mult=' m=8' if kind=='tg_x8' else ''
        if kind in ['nmos','tg','tg_x8']:switch='XN hold clk src 0 sky130_fd_pr__nfet_01v8 w=0.65 l=0.15'+mult
        if kind in ['tg','tg_x8']:switch+='\nXP hold clkb src vdd sky130_fd_pr__pfet_01v8_hvt w=1 l=0.15'+mult
        deck=f'''* Lab3 acquisition: {kind}; assumed 2pF capacitor and source resistance
.lib "{relative_spice(args.models,folder)}" tt
.temp 25
.options reltol=1e-5 abstol=1e-14 vntol=1e-8
VDD vdd 0 1.8
VIN drive 0 PWL(0 0 9n 0 9.1n {vin})
RSOURCE drive src {rs}
VCLK clk 0 PWL(0 0 10n 0 10.1n 1.8 {off}n 1.8 {off+.1}n 0 {end}n 0)
VCLKB clkb 0 PWL(0 1.8 10n 1.8 10.1n 0 {off}n 0 {off+.1}n 1.8 {end}n 1.8)
{switch}
CHOLD hold 0 2p
RHOLD hold 0 1e12
.ic v(hold)=0
.control
set wr_vecnames
set wr_singlescale
set numdgt=12
tran 20p {end}n 0 20p uic
wrdata tran.dat v(drive) v(hold) v(clk) v(src)
quit
.endc
.end
'''
        run_spice(engine,folder,deck);tr=data(folder/'tran.dat');t=tr[:,0];vh=tr[:,2]
        before=float(np.interp((off-.05)*1e-9,t,vh));after=float(np.interp((off+1)*1e-9,t,vh));later=float(np.interp((off+7)*1e-9,t,vh))
        row=dict(switch=kind,Rsource_ohm=rs,Vin_V=vin,acquisition_ns=acq,preopen_voltage_V=before,preopen_error_mV=(vin-before)*1e3,preopen_error_LSB=(vin-before)/lsb,postedge_voltage_V=after,postedge_error_mV=(vin-after)*1e3,edge_shift_mV=(after-before)*1e3,hold_change_6ns_uV=(later-after)*1e6)
        rows.append(row);waves[(kind,rs,vin,acq)]=tr
    write_csv(out/'acquisition_summary.csv',rows);(out/'acquisition_summary.json').write_text(json.dumps(rows,indent=2))
    refs=[];refwaves={}
    for cp in [20,200,2000]:
        folder=out/f'reference_{cp}pF'
        deck=f'''* Generic reference/package model; NOT a characterized SKY130 ADC/reference
VREF ideal 0 1.8
RSRC ideal n1 5
LPKG n1 ref 1n
RESR ref cap .2
CDEC cap 0 {cp}p
IPULSE ref 0 PULSE(0 .5m 10n .2n .2n 2n 100n)
.options reltol=1e-6 abstol=1e-14
.control
set wr_vecnames
set wr_singlescale
set numdgt=12
tran 5p 80n 0 5p
wrdata tran.dat v(ref) v(cap) i(VREF)
quit
.endc
.end
'''
        run_spice(engine,folder,deck);tr=data(folder/'tran.dat');t=tr[:,0];err=np.abs(tr[:,1]-1.8);bad=np.flatnonzero((t>=12.4e-9)&(err>50e-6));settle=float(t[bad[-1]+1]-12.4e-9) if len(bad) and bad[-1]+1<len(t) else 0.0 if not len(bad) else float('nan')
        refs.append(dict(Cdec_pF=cp,peak_abs_error_mV=float(err.max())*1e3,recovery_after_pulse_to_50uV_ns=settle*1e9));refwaves[cp]=tr
    write_csv(out/'reference_summary.csv',refs)
    meta=metadata(engine,args.models,'Actual ngspice runs: SKY130 switch models and an explicitly generic lumped reference-load circuit')
    meta.update(acquisition_cases=len(rows),reference_cases=len(refs),switch_dimensions_um={'nfet_W':.65,'pfet_hvt_W':1.0,'L':.15,'multiplier':{'base_cases':1,'tg_x8':8}},conditions={'corner':'tt','temperature_C':25,'supply_V':1.8,'sample_C_pF':2,'clock_edge_ns':.1,'model':'zero explicit diffusion geometry; no extracted layout'},limitations=['No transient-noise or mismatch run; kT/C is an analytical exercise, not noise visible in these deterministic traces.','Observed edge shift includes residual acquisition during the edge and model charge redistribution; it is not an isolated measurement of channel-charge injection.','Reference source R, package L, ESR and load pulse are assumed teaching parameters.'])
    (out/'run_manifest.json').write_text(json.dumps(meta,indent=2))
    plt=plot_style();fig,ax=plt.subplots(figsize=(8.5,4.6))
    for kind in ['ideal','nmos','tg']:
        tr=waves[(kind,1000,1.5,20)];ax.plot(tr[:,0]*1e9,tr[:,2],label=kind.upper())
    ax.axhline(1.5,color='#687b89',ls=':',label='input target');ax.axvline(30,color='#a4adb5',ls='--');ax.set(xlim=(9,36),xlabel='Time (ns)',ylabel='Held-node voltage (V)',title='Simulated 1.5 V acquisition: switch topology matters');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'switch_comparison.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    for kind in ['ideal','tg']:
     for rs,style in [(1000,'-'),(10000,'--')]:
        subset=[x for x in rows if x['switch']==kind and x['Rsource_ohm']==rs and x['Vin_V']==.9]
        ax.semilogy([x['acquisition_ns'] for x in subset],np.maximum(np.abs([x['preopen_error_LSB'] for x in subset]),1e-5),style+'o',label=f'{kind.upper()}, {rs/1000:g} kΩ')
    ax.axhline(.5,color='#555',ls=':',label='½ LSB, 12-bit span');ax.set(xlabel='Acquisition interval (ns)',ylabel='Absolute pre-opening error (LSB)',title='Settling before the opening edge; 0.9 V target');ax.legend(fontsize=9);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'acquisition_error.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    for cp,tr in refwaves.items():ax.plot(tr[:,0]*1e9,(tr[:,1]-1.8)*1e3,label=f'{cp:g} pF')
    ax.set(xlim=(8,35),xlabel='Time (ns)',ylabel='Reference movement (mV)',title='Generic R–L source, ESR and 0.5 mA load pulse');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'reference_transient.svg');plt.close(fig)
    selected=[x for x in rows if x['Rsource_ohm']==1000 and x['Vin_V']==1.5 and x['acquisition_ns']==20]
    print(json.dumps({'acquisition_cases':len(rows),'reference_cases':len(refs),'example':selected,'reference':refs},indent=2))
if __name__=='__main__':main()
