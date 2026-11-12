#!/usr/bin/env python3
"""Run the unmodified SKY130 HD inv_1 source netlist through DC/transient tests."""
from pathlib import Path
import argparse,csv,json,sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'common'))
from lab_support import DEFAULT_MODELS,verify_models,executable,run_spice,data,crossing,relative_spice,metadata,plot_style

def lookup(tab,slew_ns,load_pf):
    xs=np.array(tab['index_1']);ys=np.array(tab['index_2']);z=np.array(tab['values'])
    if not(xs[0]<=slew_ns<=xs[-1] and ys[0]<=load_pf<=ys[-1]):raise ValueError('Outside Liberty table')
    return float(np.interp(slew_ns,xs,[np.interp(load_pf,ys,row) for row in z]))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ngspice');ap.add_argument('--models',type=Path,default=DEFAULT_MODELS);ap.add_argument('--output',type=Path,default=HERE/'run_results');args=ap.parse_args()
    engine=executable(args.ngspice,'NGSPICE_BIN','ngspice');verify_models();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    lib=json.loads((HERE/'reference/sky130_fd_sc_hd__inv_1__tt_025C_1v80.lib.json').read_text())['pin,Y']['timing']
    conditions=[('tt',25,1.8),('ss',100,1.6),('ff',-40,1.95)]
    rows=[];waves={};curves={}
    for corner,temp,vdd in conditions:
      for load in [3.56533,9.52062,50.0]:
       for slew in [10.0,100.0]:
        name=f'{corner}_{temp}C_{load:g}fF_{slew:g}ps';folder=out/name
        ramp=slew/0.6*1e-12
        deck=f'''* Lab 1: original two-device HD inv_1 source netlist
.lib "{relative_spice(args.models,folder)}" {corner}
.include "{relative_spice(HERE/'reference/sky130_fd_sc_hd__inv_1.spice',folder)}"
.temp {temp}
.options reltol=1e-5 abstol=1e-14 vntol=1e-8
VDD vdd 0 {vdd}
VIN a 0 PULSE(0 {vdd} 0.5n {ramp:.12g} {ramp:.12g} 3n 8n)
XINV a 0 0 vdd vdd y sky130_fd_sc_hd__inv_1
CLOAD y 0 {load}f
.control
set wr_vecnames
set wr_singlescale
set numdgt=12
dc VIN 0 {vdd} 0.002
wrdata dc.dat v(a) v(y) i(VDD)
tran 1p 7n 0 1p
wrdata tran.dat v(a) v(y) i(VDD)
quit
.endc
.end
'''
        run_spice(engine,folder,deck);tr=data(folder/'tran.dat');dc=data(folder/'dc.dat');t,vi,vo,iv=tr.T
        ir=crossing(t,vi,vdd/2,True);iff=crossing(t,vi,vdd/2,False)
        of=crossing(t,vo,vdd/2,False,after=.5e-9);orr=crossing(t,vo,vdd/2,True,after=3e-9)
        slewout_r=(crossing(t,vo,.8*vdd,True,after=3e-9)-crossing(t,vo,.2*vdd,True,after=3e-9))*1e12
        slewout_f=(crossing(t,vo,.2*vdd,False,after=.5e-9)-crossing(t,vo,.8*vdd,False,after=.5e-9))*1e12
        energy=float(np.trapezoid(-vdd*iv,t))*1e15
        vtrip=float(np.interp(0,(dc[:,1]-dc[:,2]),dc[:,1]))
        row=dict(corner=corner,temp_C=temp,VDD_V=vdd,load_fF=load,input_slew_20_80_ps=slew,
           tphl_ps=(of-ir)*1e12,tplh_ps=(orr-iff)*1e12,output_rise_20_80_ps=slewout_r,
           output_fall_80_20_ps=slewout_f,supply_energy_fJ=energy,peak_supply_current_uA=float(np.max(-iv))*1e6,
           dc_trip_V=vtrip,liberty_tphl_ps='',liberty_tplh_ps='')
        if corner=='tt':
            row['liberty_tphl_ps']=1000*lookup(lib['cell_fall,del_1_7_7'],slew/1000,load/1000)
            row['liberty_tplh_ps']=1000*lookup(lib['cell_rise,del_1_7_7'],slew/1000,load/1000)
        if min(row['tphl_ps'],row['tplh_ps'],slewout_r,slewout_f)<=0:raise RuntimeError('Unexpected timing polarity')
        rows.append(row);waves[(corner,load,slew)]=tr;curves[corner]=dc
    with (out/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    meta=metadata(engine,args.models,'Actual ngspice DC/transient simulation of unmodified SKY130 source-netlist inverter')
    meta.update(cases=len(rows),standard_cell_revision='ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1',measurement_definitions={'delay':'50% input to 50% output, opposite polarity','slew':'20% to 80% or 80% to 20%','energy':'integral of -VDD*i(VDD) over 0..7ns; one complete output discharge/recharge cycle'},limitations=['Source-level two-MOS cell; no extracted local interconnect or physical junction geometry supplied.','Different simulator/model preparation from original Liberty characterization; comparison is not reproduction of the characterized library.','No statistical mismatch, aged-device, routing, EM or signoff analysis.'])
    (out/'run_manifest.json').write_text(json.dumps(meta,indent=2));(out/'summary.json').write_text(json.dumps(rows,indent=2))
    plt=plot_style()
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    for c,_,_ in conditions:ax.plot(curves[c][:,1],curves[c][:,2],label=c.upper())
    ax.set(xlabel='Input voltage (V)',ylabel='Output voltage (V)',title='Simulated DC transfer: three specified PVT combinations');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/'dc_transfer.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    for c,_,_ in conditions:
        subset=[x for x in rows if x['corner']==c and x['input_slew_20_80_ps']==10]
        ax.plot([x['load_fF'] for x in subset],[x['tplh_ps'] for x in subset],'-o',label=c.upper()+' simulated rise')
    tt=[x for x in rows if x['corner']=='tt' and x['input_slew_20_80_ps']==10]
    ax.plot([x['load_fF'] for x in tt],[x['liberty_tplh_ps'] for x in tt],'k--',label='TT published Liberty rise')
    ax.set(xlabel='External load (fF)',ylabel='50% propagation delay (ps)',title='Source-netlist simulation and archived characterization differ');ax.legend(fontsize=9);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'delay_load.svg');plt.close(fig)
    tr=waves[('tt',9.52062,10.0)];fig,axes=plt.subplots(2,1,figsize=(8.5,6),sharex=True)
    axes[0].plot(tr[:,0]*1e9,tr[:,1],label='input');axes[0].plot(tr[:,0]*1e9,tr[:,2],label='output');axes[0].set(ylabel='Voltage (V)',title='TT / 25°C / 1.8 V / 9.52062 fF / 10 ps input slew');axes[0].legend()
    axes[1].plot(tr[:,0]*1e9,-tr[:,3]*1e6);axes[1].set(xlabel='Time (ns)',ylabel='Supply current (µA)');axes[1].set_xlim(.35,4.3)
    for ax in axes:ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'transient_current.svg');plt.close(fig)
    nominal=next(x for x in rows if x['corner']=='tt' and x['load_fF']==9.52062 and x['input_slew_20_80_ps']==10)
    print(json.dumps({'cases':len(rows),'nominal':nominal,'results':str(out)},indent=2))

if __name__=='__main__':main()
