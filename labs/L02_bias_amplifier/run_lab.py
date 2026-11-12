#!/usr/bin/env python3
"""L02: run actual SKY130 mirror/amplifier experiments and separate behavioral startup cases.

Python standard library only. Requires ngspice and the course's common model library.
Run: NGSPICE_BIN=/path/to/ngspice python3 run_lab.py
The generated SPICE decks are directly runnable from their results directory.
"""
from __future__ import annotations
import argparse, csv, datetime, hashlib, html, json, math, os, re, shutil, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'common'))
from spice_paths import portable_library_paths
DEFAULT_MODELS=HERE.parent/'common'/'models'/'sky130_course.lib.spice'
COLORS=['#2b6cb0','#a75b34','#397454','#77559b','#597d91','#b34361']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def template(name,values):
    s=(HERE/'circuits'/name).read_text()
    for k,v in values.items():s=s.replace('@'+k+'@',str(v))
    missing=re.findall(r'@[A-Z_]+@',s)
    if missing:raise ValueError('Unresolved template fields: '+str(missing))
    return s

def load_dat(path,columns):
    rows=[]
    for line in Path(path).read_text().splitlines():
        fields=line.split()
        try:vals=[float(x) for x in fields]
        except ValueError:continue
        if len(vals)!=len(columns)+1:raise ValueError(f'{path}: expected {len(columns)+1} columns, got {len(vals)}')
        if not all(math.isfinite(v) for v in vals):raise ValueError(f'{path}: nonfinite result')
        rows.append(dict(zip(['scale']+columns,vals)))
    if not rows:raise ValueError(f'No numeric results in {path}')
    return rows

def save_csv(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def interp(rows,xkey,ykey,x):
    for a,b in zip(rows,rows[1:]):
        if a[xkey]<=x<=b[xkey]:
            return a[ykey]+(b[ykey]-a[ykey])*(x-a[xkey])/(b[xkey]-a[xkey])
    raise ValueError('Interpolation outside data range')

def crossings(rows,key,target):
    out=[]
    for a,b in zip(rows,rows[1:]):
        ya,yb=a[key]-target,b[key]-target
        if ya==0:out.append(a['scale'])
        elif ya*yb<0:out.append(a['scale']+(b['scale']-a['scale'])*(-ya)/(yb-ya))
    return out

def intervals(rows,test):
    out=[];start=None;prev=None
    for row in rows:
        if test(row):
            if start is None:start=row['vout']
            prev=row['vout']
        elif start is not None:out.append([start,prev]);start=prev=None
    if start is not None:out.append([start,prev])
    return out

def nice_ticks(lo,hi,target=6):
    """Round tick values (1, 2, 2.5 or 5 times a power of ten) covering [lo, hi]."""
    raw=(hi-lo)/max(1,target);mag=10**math.floor(math.log10(raw))
    step=min((m*mag for m in (1,2,2.5,5,10) if m*mag>=raw*0.999),default=10*mag)
    first=math.ceil(lo/step-1e-9)*step
    return [round(first+i*step,12) for i in range(int((hi-first)/step+1e-9)+1)]

def tick_label(val,logx=False):
    if logx:
        for exp,suffix in ((9,'G'),(6,'M'),(3,'k'),(0,'')):
            if abs(val)>=10**exp:return f'{val/10**exp:g}{suffix}'
    return f'{val:g}'

def plot(path,title,subtitle,series,xlabel,ylabel,xlim,ylim,logx=False,xticks=None,yticks=None,hlines=()):
    """Original vector chart from captured numeric data; no plotting dependencies."""
    W,H=860,460;L,R,T,B=88,25,(103 if len(series)>3 else 86),74;pw,ph=W-L-R,H-T-B
    xtrans=math.log10 if logx else lambda x:x
    xmin,xmax=map(xtrans,xlim);ymin,ymax=ylim
    X=lambda x:L+(xtrans(x)-xmin)/(xmax-xmin)*pw
    Y=lambda y:T+(ymax-y)/(ymax-ymin)*ph
    esc=html.escape
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle)}</desc><style>text{{font-family:system-ui,sans-serif;fill:#26313c}}.small{{font-size:12px}}.tick{{font-size:11px;fill:#536879}}</style><rect width="860" height="460" fill="white"/>',f'<text x="{L}" y="25" font-size="18" font-weight="650">{esc(title)}</text>',f'<text x="{L}" y="46" class="small">{esc(subtitle)}</text>',f'<defs><clipPath id="plotclip"><rect x="{L}" y="{T}" width="{pw}" height="{ph}"/></clipPath></defs>']
    if xticks is None:xticks=nice_ticks(xlim[0],xlim[1],7)
    if yticks is None:yticks=nice_ticks(ymin,ymax,9)
    for val in xticks:
        if not xlim[0]<=val<=xlim[1]:continue
        x=X(val);label=tick_label(val,logx)
        s += [f'<line x1="{x:.2f}" y1="{T}" x2="{x:.2f}" y2="{T+ph}" stroke="#e3e9ef"/>',f'<text x="{x:.2f}" y="{T+ph+23}" text-anchor="middle" class="tick">{label}</text>']
    for val in yticks:
        y=Y(val);s += [f'<line x1="{L}" y1="{y:.2f}" x2="{L+pw}" y2="{y:.2f}" stroke="#e3e9ef"/>',f'<text x="{L-10}" y="{y+4:.2f}" text-anchor="end" class="tick">{val:g}</text>']
    for v in hlines:s.append(f'<line x1="{L}" y1="{Y(v):.2f}" x2="{L+pw}" y2="{Y(v):.2f}" stroke="#98a5b2" stroke-dasharray="6 4"/>')
    for i,(label,data) in enumerate(series):
        pts=' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in data if xlim[0]<=x<=xlim[1] and (not logx or x>0))
        c=COLORS[i%len(COLORS)];s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.3" clip-path="url(#plotclip)"/>')
        lx=L+(i%3)*250;ly=66+(i//3)*17
        s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+26}" y2="{ly}" stroke="{c}" stroke-width="3"/><text x="{lx+34}" y="{ly+4}" class="small">{esc(label)}</text>')
    s += [f'<rect x="{L}" y="{T}" width="{pw}" height="{ph}" fill="none" stroke="#b4c1cd"/>',f'<text x="{L+pw/2}" y="{H-16}" text-anchor="middle" font-size="14">{esc(xlabel)}</text>',f'<text x="22" y="{T+ph/2}" transform="rotate(-90,22,{T+ph/2})" text-anchor="middle" font-size="14">{esc(ylabel)}</text>','</svg>']
    Path(path).write_text(''.join(s))

class Runner:
    def __init__(self,args):
        self.args=args;self.out=Path(args.output).expanduser().resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.exe=args.ngspice or os.environ.get('NGSPICE_BIN') or shutil.which('ngspice')
        if not self.exe:raise SystemExit('ngspice not found. Install it or set NGSPICE_BIN=/path/to/ngspice.')
        found=shutil.which(self.exe);self.exe=str(Path(found or self.exe).expanduser().resolve())
        if not Path(self.exe).is_file():raise SystemExit('ngspice executable not found: '+self.exe)
        self.models=Path(args.models).expanduser().resolve();self.records=[]
        if not args.behavioral_only and not self.models.is_file():raise SystemExit('Common model file missing. Run the course model bootstrap or pass --models PATH.')
        self.model_ref=os.path.relpath(self.models,self.out).replace(os.sep,'/')
        self.shared={'MODELS':self.model_ref,'CORNER':args.corner,'TEMP':args.temperature}
        self.version=subprocess.run([self.exe,'--version'],capture_output=True,text=True,check=True).stdout.strip()
    def run(self,name,which,values,columns):
        vals={**self.shared,**values,'DATA':name+'.dat'};text=portable_library_paths(template(which,vals),self.out)
        deck=self.out/(name+'.cir');deck.write_text(text)
        proc=subprocess.run([self.exe,'-b',deck.name],cwd=self.out,capture_output=True,text=True,timeout=120)
        log=proc.stdout+'\n'+proc.stderr;(self.out/(name+'.log')).write_text(log)
        raw=self.out/(name+'.dat')
        if proc.returncode!=0 or not raw.exists() or re.search(r'(?im)^(fatal error|error:|fatal:)',log):
            raise RuntimeError(f'{name} failed; inspect {name}.log\n{log[-2500:]}')
        rows=load_dat(raw,columns);save_csv(self.out/(name+'.csv'),rows)
        self.records.append({'case':name,'template':which,'deck_sha256':sha(deck),'raw_sha256':sha(raw),'csv_sha256':sha(self.out/(name+'.csv')),'rows':len(rows),'exit_status':proc.returncode})
        return rows
    def amp(self,name,vin,analysis='op',clamp=None,cload='1p',source=None):
        if analysis.startswith('ac'):
            expressions='let gain_real=real(v(out))\nlet gain_imag=imag(v(out))'
            columns=['gain_real','gain_imag']
        else:
            expressions='let vin_value=v(vin)\nlet vout=v(out)\nlet vbiasp=v(vbiasp)\nlet id_n=i(vnsense)\nlet id_p=i(vpsense)\nlet supply_current=-i(vdd)'
            columns=['vin_value','vout','vbiasp','id_n','id_p','supply_current']
        vals={'INPUT_SOURCE':source or f'DC {vin:.12g} AC 1','CLOAD':cload,'CLAMP':'' if clamp is None else f'VCLAMP out 0 {clamp:.12g}','ANALYSIS':analysis,'EXPRESSIONS':expressions,'VECTORS':' '.join(columns)}
        return self.run(name,'amplifier.cir.in',vals,columns)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--models',default=str(DEFAULT_MODELS));ap.add_argument('--ngspice')
    ap.add_argument('--corner',choices=['tt','ff','ss'],default='tt');ap.add_argument('--temperature',type=float,default=25)
    ap.add_argument('--output',default=str(HERE/'run_results'));ap.add_argument('--bias',type=float,help='Fixed amplifier input bias; omit to center the nominal output at 0.9 V.')
    ap.add_argument('--behavioral-only',action='store_true',help='Run only the separate startup model; no SKY130 models needed.')
    args=ap.parse_args();r=Runner(args)
    metrics={'status':'actually_executed','corner':args.corner,'temperature_c':args.temperature,'supply_v':1.8,'reference_current_a':20e-6,'geometry_scope':'W/L are supported model-bin values in micrometres. Source/drain rectangles assume0.29um extension; no layout extraction.','startup_scope':'Separate phenomenological ODE; no SKY130 transistor or bandgap performance is inferred.'}
    if not args.behavioral_only:
        mirrors={};mirror_metrics={}
        for label,L in [('long',1.0),('short',0.15)]:
            rows=r.run('mirror_'+label,'mirror.cir.in',{'LENGTH':L},['vout','vgate','iout']);mirrors[label]=rows
            i09=interp(rows,'vout','iout',.9);di=interp(rows,'vout','iout',.905)-interp(rows,'vout','iout',.895)
            mirror_metrics[label]={'width_um':5,'length_um':L,'gate_bias_v':rows[0]['vgate'],'output_current_at_0p9v_a':i09,'ratio_at_0p9v':i09/20e-6,'within_5pct_of_20uA_intervals_v':intervals(rows,lambda z:abs(z['iout']/20e-6-1)<=.05),'rout_near_0p9v_ohm':.01/di,'sweep_step_v':.005}
        metrics['mirror']=mirror_metrics
        plot(r.out/'mirror_compliance.svg','NMOS mirror compliance: captured SKY130 results',f'{args.corner.upper()}, {args.temperature:g} °C, VDD=1.8 V, IREF=20 µA; W=5 µm for both devices in each pair',[(f'L={L:g} µm',[(z['vout'],z['iout']/20e-6) for z in mirrors[label]]) for label,L in [('long',1),('short',.15)]],'Forced output voltage (V)','IOUT / IREF',(0,1.8),(0,2),xticks=[0,.3,.6,.9,1.2,1.5,1.8],yticks=[0,.5,1,1.5,2],hlines=(.95,1,1.05))
        transfer=r.amp('amplifier_transfer',.7,'dc VSIG 0.4 1.2 0.002')
        if args.bias is None:
            lo,hi=.4,1.2
            for i in range(23):
                mid=(lo+hi)/2;q=r.amp(f'calibration_{i:02d}',mid,clamp=.9)[0]
                if q['id_n']<q['id_p']:lo=mid
                else:hi=mid
            bias=(lo+hi)/2;bias_mode='calibrated_to_0p9v_output_at_this_corner'
        else:bias=args.bias;bias_mode='user_fixed_bias'
        op=r.amp('amplifier_op',bias)[0];vo=op['vout'];dv=1e-4
        gi=r.amp('gm_plus',bias+dv,clamp=vo)[0];gj=r.amp('gm_minus',bias-dv,clamp=vo)[0]
        oi=r.amp('gds_plus',bias,clamp=vo+dv)[0];oj=r.amp('gds_minus',bias,clamp=vo-dv)[0]
        gm=(gi['id_n']-gj['id_n'])/(2*dv);gn=(oi['id_n']-oj['id_n'])/(2*dv);gp=-(oi['id_p']-oj['id_p'])/(2*dv)
        amp={'bias_input_v':bias,'bias_mode':bias_mode,'operating_point':op,'perturbation_v':dv,'gm_n_s':gm,'gds_n_s':gn,'gds_p_s':gp,'ro_n_ohm':1/gn,'ro_p_ohm':1/gp,'predicted_low_frequency_gain_v_per_v':-gm/(gn+gp)}
        acs={}
        for name,cap in [('1pF','1p'),('10pF','10p')]:
            rows=r.amp('amplifier_ac_'+name,bias,'ac dec 80 10 100meg',cload=cap)
            for z in rows:
                gain=complex(z['gain_real'],z['gain_imag']);z['gain_magnitude']=abs(gain);z['gain_db']=20*math.log10(abs(gain));phase=math.degrees(math.atan2(gain.imag,gain.real));z['phase_deg']=phase if phase<=0 else phase-360
            save_csv(r.out/('amplifier_ac_'+name+'.csv'),rows);acs[name]=rows
            target=rows[0]['gain_magnitude']/math.sqrt(2);f3=crossings(rows,'gain_magnitude',target)
            amp['ac_'+name]={'gain_at_10hz_v_per_v':rows[0]['gain_real'],'magnitude_at_10hz':rows[0]['gain_magnitude'],'bandwidth_3db_hz':f3[0] if f3 else None}
        amp['ac_vs_dc_derivative_relative_error']=abs(amp['ac_1pF']['gain_at_10hz_v_per_v']/amp['predicted_low_frequency_gain_v_per_v']-1)
        transients={}
        for label,amplitude in [('small',.0005),('large',.05)]:
            src=f'DC {bias:.12g} SIN({bias:.12g} {amplitude:.12g} 10k)'
            rows=r.amp('amplifier_transient_'+label,bias,'tran 100n 500u 0 100n',source=src);transients[label]=rows
            tail=[z for z in rows if z['scale']>=.0003];vmin=min(z['vout'] for z in tail);vmax=max(z['vout'] for z in tail)
            amp['transient_'+label]={'input_amplitude_v':amplitude,'frequency_hz':10000,'output_min_last_two_cycles_v':vmin,'output_max_last_two_cycles_v':vmax,'amplitude_ratio_last_two_cycles':(vmax-vmin)/(2*amplitude),'ratio_scope':'Peak-to-peak amplitude ratio, not a distortion or linear-gain measurement for the large case.'}
        metrics['amplifier']=amp
        plot(r.out/'amplifier_transfer.svg','Open-loop amplifier transfer: captured SKY130 results',f'{args.corner.upper()}, {args.temperature:g} °C; DC input sweep, with ideal reference current and 1.8 V supply', [('VOUT',[(z['vin_value'],z['vout']) for z in transfer])],'Input voltage (V)','Output voltage (V)',(.4,1.2),(0,1.8),hlines=(.9,))
        plot(r.out/'amplifier_gain.svg','AC gain changes with capacitive load',f'Captured SKY130 small-signal AC analysis at VIN={bias:.6f} V; AC input magnitude 1 is normalization',[(name,[(z['scale'],z['gain_db']) for z in rows]) for name,rows in acs.items()],'Frequency (Hz, logarithmic)','Gain magnitude (dB)',(10,1e8),(-40,60),True,[10,100,1000,1e4,1e5,1e6,1e7,1e8],[-40,-20,0,20,40,60])
        plot(r.out/'amplifier_phase.svg','AC phase of the inverting common-source stage','Captured SKY130 data; phase is represented on the negative-angle branch',[(name,[(z['scale'],z['phase_deg']) for z in rows]) for name,rows in acs.items()],'Frequency (Hz, logarithmic)','Output/input phase (degrees)',(10,1e8),(-300,-150),True,[10,100,1000,1e4,1e5,1e6,1e7,1e8],[-300,-270,-240,-210,-180,-150])
        plot(r.out/'amplifier_transient.svg','Small and large input signals: captured SKY130 results','Both at 10 kHz and 1 pF load; the large case must not be interpreted using the small-signal gain',[('0.5 mV input amplitude',[(z['scale']*1e6,z['vout']) for z in transients['small']]),('50 mV input amplitude',[(z['scale']*1e6,z['vout']) for z in transients['large']])],'Time (µs)','Output voltage (V)',(300,500),(0,1.8),hlines=(.9,))
    startups={};sm={}
    cases=[
      ('no_startup','PWL(0 0 10u 1.8 5m 1.8)',0,'0'),
      ('forced_initial','DC 1.8',.8,'0'),
      ('fast_ramp','PWL(0 0 10u 1.8 5m 1.8)',0,'1'),
      ('slow_ramp','PWL(0 0 1m 1.8 5m 1.8)',0,'1'),
      ('brownout_rearmed','PWL(0 0 10u 1.8 2m 1.8 2.01m 0.2 2.5m 0.2 2.51m 1.8 5m 1.8)',0,'1'),
      ('brownout_timed_kick','PWL(0 0 10u 1.8 2m 1.8 2.01m 0.2 2.5m 0.2 2.51m 1.8 5m 1.8)',0,'0.5*(1-tanh((time-300u)/5u))')]
    for name,supply,initial,kick in cases:
        rows=r.run('startup_'+name,'startup_behavioral.cir.in',{'SUPPLY':supply,'INITIAL':initial,'KICK_GATE':kick},['supply','state','reference','kick_current']);startups[name]=rows
        ready=[z['scale'] for z in rows if z['reference']>=1.188]
        recovery=[z['scale'] for z in rows if z['scale']>=.00251 and z['reference']>=1.188]
        sm[name]={'initial_normalized_state':initial,'final_reference_v':rows[-1]['reference'],'first_99pct_crossing_s':ready[0] if ready else None,'after_brownout_99pct_crossing_s':recovery[0] if name.startswith('brownout') and recovery else None,'scope':'Behavioral result; threshold crossings are not a physical ready specification.'}
    metrics['behavioral_startup']=sm
    plot(r.out/'startup_powerup.svg','Startup state matters: behavioral model only','No transistor, BJT, bandgap or SKY130 startup performance is represented',[(label,[(z['scale']*1e3,z['reference']) for z in startups[key]]) for key,label in [('no_startup','No startup, x(0)=0'),('forced_initial','Forced x(0)=0.8'),('fast_ramp','Kick, 10 µs supply ramp'),('slow_ramp','Kick, 1 ms supply ramp')]],'Time (ms)','Behavioral reference (V)',(0,1.5),(0,1.4),hlines=(1.2,))
    plot(r.out/'startup_brownout.svg','A startup kick must work again after a brownout','Separate behavioral ODE; the timed one-shot ends before the second power event',[(label,[(z['scale']*1e3,z['reference']) for z in startups[key]]) for key,label in [('brownout_rearmed','State-qualified kick'),('brownout_timed_kick','Kick only during first 300 µs')]],'Time (ms)','Behavioral reference (V)',(1.8,3.2),(0,1.4),hlines=(1.2,))
    for record in r.records:record['csv_sha256']=sha(r.out/(record['case']+'.csv'))
    provenance={'run_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'simulator_version':r.version,'simulator_executable_sha256':sha(r.exe),'python_version':os.sys.version,'corner':args.corner,'temperature_c':args.temperature,'model_wrapper':r.model_ref,'model_wrapper_sha256':sha(r.models) if r.models.is_file() else None,'runner_sha256':sha(__file__),'templates':{p.name:sha(p) for p in (HERE/'circuits').glob('*.in')},'cases':r.records}
    manifest=r.models.parent/'source_manifest.json'
    if manifest.exists():
        upstream=json.loads(manifest.read_text());provenance['upstream_revision']=upstream.get('revision');provenance['source_manifest_sha256']=sha(manifest)
        checked=[]
        for item in upstream.get('files',[]):
            candidate=r.models.parent/'upstream'/item['path']
            if candidate.exists():checked.append({'path':item['path'],'sha256':sha(candidate),'matches_manifest':sha(candidate)==item['sha256']})
        provenance['checked_upstream_files']=checked
        if not all(z['matches_manifest'] for z in checked):raise RuntimeError('An upstream model file differs from its manifest. Do not compare this run as the same model revision.')
    (r.out/'metrics.json').write_text(json.dumps(metrics,indent=2));(r.out/'provenance.json').write_text(json.dumps(provenance,indent=2))
    checks={'all_cases_exited_successfully':all(z['exit_status']==0 for z in r.records),'startup_zero_state_stays_low':sm['no_startup']['final_reference_v']<.01,'startup_kick_reaches_high':abs(sm['fast_ramp']['final_reference_v']-1.2)<.012,'rearmed_startup_recovers':abs(sm['brownout_rearmed']['final_reference_v']-1.2)<.012,'timed_startup_does_not_recover':sm['brownout_timed_kick']['final_reference_v']<.01}
    if not args.behavioral_only:
        checks['dc_derivative_matches_ac_within_2pct']=metrics['amplifier']['ac_vs_dc_derivative_relative_error']<.02
        checks['larger_load_reduces_bandwidth']=metrics['amplifier']['ac_10pF']['bandwidth_3db_hz']<metrics['amplifier']['ac_1pF']['bandwidth_3db_hz']
        if args.bias is None:checks['calibrated_bias_within_1mV']=abs(metrics['amplifier']['operating_point']['vout']-.9)<.001
    (r.out/'checks.json').write_text(json.dumps(checks,indent=2))
    if not all(checks.values()):raise RuntimeError('One or more consistency checks failed; inspect checks.json and raw data.')
    print(json.dumps({'status':'completed','cases':len(r.records),'output':str(r.out),'checks':checks,'amplifier':metrics.get('amplifier'),'mirror':metrics.get('mirror'),'startup':sm},indent=2))
if __name__=='__main__':main()
