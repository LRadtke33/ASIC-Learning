#!/usr/bin/env python3
"""Lab 4: geometry -> analytical RC estimate -> reproducible transient response.

This is an educational estimator, NOT a foundry-qualified extractor, DRC deck,
LVS tool, field solver, transistor simulation, or a Magic extraction result.
Only the Python standard library is required. ngspice is optional; shipped
reference results were produced with ngspice 44.2. All geometry is in um.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, html, json, math, os
from pathlib import Path
import shutil, subprocess, sys

HERE = Path(__file__).resolve().parent
COLORS = ['#2b6cb0', '#a56830', '#7a4ea3', '#168166']
SOURCE_R = 20000.0       # assumed driver/bias resistance, ohms
LOAD_C = 50e-15         # assumed receiver capacitance, farads
VSTEP = 1.8             # assumed stimulus amplitude, volts
START = 2e-9
RISE = 0.2e-9
STOP = 60e-9
HALF_LSB = VSTEP / 8192 # illustrative 12-bit half-LSB requirement


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def area_overlap(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))


def validate(g):
    p, w = g['path_um'], g['width_um']
    if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0:
        raise ValueError('width_um must be positive and finite')
    if len(p) < 2 or any(len(q) != 2 or not all(math.isfinite(v) for v in q) for q in p):
        raise ValueError('path_um requires at least two finite (x,y) points')
    strips = []
    for a, b in zip(p, p[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        if (dx == 0) == (dy == 0):
            raise ValueError('Only nonzero Manhattan segments are supported')
        if abs(dx)+abs(dy) < w:
            raise ValueError('Each segment must be at least one wire width long')
        strips.append([min(a[0],b[0])-w/2, min(a[1],b[1])-w/2,
                       max(a[0],b[0])+w/2, max(a[1],b[1])+w/2])
    for i, a in enumerate(strips):
        for j, b in enumerate(strips):
            if j > i+1 and area_overlap(a,b) > 0:
                raise ValueError('Self-touching/crossing routes need a polygon extractor; unsupported here')
    plane = g['reference_plane_met2_um']
    if any(x-w/2 < plane[0] or x+w/2 > plane[2] or y-w/2 < plane[1] or y+w/2 > plane[3] for x,y in p):
        raise ValueError('Reference plane must enclose the complete route')
    regions = g.get('aggressor_met4_um', []) + g.get('grounded_patch_met4_um', [])
    for r in regions:
        if len(r) != 4 or r[2] <= r[0] or r[3] <= r[1]:
            raise ValueError('Upper regions must be nonempty rectangles')
    for i, a in enumerate(regions):
        for b in regions[i+1:]:
            if area_overlap(a,b) > 0:
                raise ValueError('Upper rectangles must not overlap or short different nets')
    for a,b in zip(p,p[1:]):
        horizontal = a[1] == b[1]
        stripe = ([min(a[0],b[0]),a[1]-w/2,max(a[0],b[0]),a[1]+w/2]
                  if horizontal else [a[0]-w/2,min(a[1],b[1]),a[0]+w/2,max(a[1],b[1])])
        for r in regions:
            if area_overlap(stripe,r)>0:
                full_width = (r[1] <= stripe[1] and r[3] >= stripe[3]) if horizontal else (r[0] <= stripe[0] and r[2] >= stripe[2])
                if not full_width:
                    raise ValueError('Upper region must span the full wire width where it overlaps; partial lateral coverage is unsupported')


def overlap_length(a, b, rectangles):
    """Centerline coverage, valid here because each upper rectangle spans width.
    Upper edge/fringing fields are deliberately not estimated.
    """
    total = 0.0
    for x0,y0,x1,y1 in rectangles:
        if a[1] == b[1] and y0 < a[1] < y1:
            total += max(0, min(max(a[0],b[0]),x1)-max(min(a[0],b[0]),x0))
        elif a[0] == b[0] and x0 < a[0] < x1:
            total += max(0, min(max(a[1],b[1]),y1)-max(min(a[1],b[1]),y0))
    return total


def estimate(g, coeff, segment_um):
    validate(g)
    w = g['width_um']
    pts = [tuple(g['path_um'][0])]
    for a,b in zip(g['path_um'], g['path_um'][1:]):
        length = abs(b[0]-a[0])+abs(b[1]-a[1])
        count = max(1, math.ceil(length/segment_um))
        pts += [(a[0]+(b[0]-a[0])*i/count, a[1]+(b[1]-a[1])*i/count) for i in range(1,count+1)]
    n = len(pts)
    cg, cc = [0.0]*n, [0.0]*n
    resistance, elements = [], []
    total_length = 0.0
    total_agg_area = total_fill_area = 0.0
    rs = coeff['met3_sheet_ohm_per_square']
    c_down = coeff['met2_met3_area_aF_per_um2']*1e-18
    c_fringe = coeff['met3_to_met2_downward_fringe_aF_per_um']*1e-18
    c_up = coeff['met3_met4_area_aF_per_um2']*1e-18
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        length = abs(b[0]-a[0])+abs(b[1]-a[1])
        r = rs*length/w
        agg_area = overlap_length(a,b,g.get('aggressor_met4_um',[]))*w
        fill_area = overlap_length(a,b,g.get('grounded_patch_met4_um',[]))*w
        cground = length*(c_down*w+2*c_fringe)+c_up*fill_area
        cmutual = c_up*agg_area
        resistance.append(r)
        for j in (i,i+1):
            cg[j] += cground/2
            cc[j] += cmutual/2
        total_length += length
        total_agg_area += agg_area
        total_fill_area += fill_area
        elements.append({'from':i,'to':i+1,'length_um':length,'R_ohm':r,
                         'ground_C_F':cground,'mutual_C_F':cmutual,
                         'aggressor_overlap_um2':agg_area,'grounded_patch_overlap_um2':fill_area})
    # Count only the two physical end edges. Numerical section boundaries
    # create no additional wire perimeter and hence no additional fringe C.
    cg[0] += c_fringe*w
    cg[-1] += c_fringe*w
    expected_r = rs*total_length/w
    expected_cg = c_down*total_length*w+c_fringe*(2*total_length+2*w)+c_up*total_fill_area
    assert math.isclose(sum(resistance),expected_r,rel_tol=1e-12)
    assert math.isclose(sum(cg),expected_cg,rel_tol=1e-12)
    assert math.isclose(sum(cc),c_up*total_agg_area,abs_tol=1e-30,rel_tol=1e-12)
    assert all(r>0 for r in resistance) and all(c>0 for c in cg)
    return {'id':g['id'],'label':g['label'],'points_um':pts,'R_ohm':resistance,
            'Cg_F':cg,'Cc_F':cc,'elements':elements,'length_um':total_length,'width_um':w,
            'total_R_ohm':sum(resistance),'total_ground_C_fF':sum(cg)*1e15,
            'total_mutual_C_fF':sum(cc)*1e15,'aggressor_overlap_um2':total_agg_area,
            'grounded_patch_overlap_um2':total_fill_area,'node_count':n,
            'load_C_fF':LOAD_C*1e15,'source_R_ohm':SOURCE_R}


def node_name(i,n):
    return 'SIG_DRV' if i == 0 else 'SIG_RX' if i == n-1 else f'SIG_{i:03d}'


def vector(i,n):
    return f'v({node_name(i,n).lower()})' if i in (0,n-1) else f'v(xroute.{node_name(i,n).lower()})'


def write_network(net, out):
    n = net['node_count']
    lines = ['* Educational geometry-derived RC ESTIMATE, not foundry extraction.',
             '* Coefficients and omitted mechanisms: ../../sky130_coefficients.json',
             '.subckt ROUTE SIG_DRV SIG_RX AGG REF']
    for i,r in enumerate(net['R_ohm']):
        lines.append(f'Rseg{i:03d} {node_name(i,n)} {node_name(i+1,n)} {r:.12g}')
    for i,(cg,cc) in enumerate(zip(net['Cg_F'],net['Cc_F'])):
        lines.append(f'Cg{i:03d} {node_name(i,n)} REF {cg:.12e}')
        if cc:
            lines.append(f'Cc{i:03d} {node_name(i,n)} AGG {cc:.12e}')
    lines.append('.ends ROUTE')
    (out/'networks'/f"{net['id']}.spice").write_text('\n'.join(lines)+'\n')
    with (out/'mapping'/f"{net['id']}_probes.csv").open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['schematic_net','physical_role','spice_node','ngspice_vector','x_um','y_um','path_node_index'])
        for i,(x,y) in enumerate(net['points_um']):
            role='driver_terminal' if i==0 else 'receiver_terminal' if i==n-1 else 'interconnect_internal'
            wr.writerow(['SIG',role,node_name(i,n),vector(i,n),f'{x:.9g}',f'{y:.9g}',i])


def ramp(t):
    return VSTEP*min(1.0,max(0.0,(t-START)/RISE))


def builtin_transient(net, kind, h):
    """Backward Euler, tridiagonal passive ladder, explicitly labeled in output.
    Cc is retained to the driven AGG terminal, not silently grounded.
    This discrete equation is C/dt*(vnew-vold)+G*vnew =
    gsrc*Vsrc_new + Cc/dt*(Vagg_new-Vagg_old).
    """
    n = net['node_count']; cap = [a+b for a,b in zip(net['Cg_F'],net['Cc_F'])]
    cap[-1] += LOAD_C
    conductance=[1/r for r in net['R_ohm']]
    gs=1/SOURCE_R
    diag=[cap[i]/h+(conductance[i-1] if i>0 else gs)+(conductance[i] if i<n-1 else 0) for i in range(n)]
    lower=[-v for v in conductance]; upper=lower[:]
    den=[diag[0]]; prime=[upper[0]/den[0]]
    for i in range(1,n):
        den.append(diag[i]-lower[i-1]*prime[i-1])
        if i<n-1:prime.append(upper[i]/den[i])
    old=[0.0]*n; old_agg=0.0; rows=[];mid=n//2
    steps=round(STOP/h)
    for k in range(steps+1):
        t=k*h; source=ramp(t) if kind=='step' else 0.0; agg=ramp(t) if kind=='coupling' else 0.0
        rhs=[cap[i]/h*old[i]+net['Cc_F'][i]/h*(agg-old_agg) for i in range(n)]
        rhs[0]+=gs*source
        dp=[rhs[0]/den[0]]
        for i in range(1,n):dp.append((rhs[i]-lower[i-1]*dp[i-1])/den[i])
        v=[0.0]*n;v[-1]=dp[-1]
        for i in range(n-2,-1,-1):v[i]=dp[i]-prime[i]*v[i+1]
        rows.append([t,source,v[0],v[mid],v[-1],agg]);old=v;old_agg=agg
    return rows


def write_deck(net, kind, out, h):
    ident=net['id'];mid=net['node_count']//2
    pwl=f'PWL(0 0 {START:.12g} 0 {START+RISE:.12g} {VSTEP} {STOP:.12g} {VSTEP})'
    src=pwl if kind=='step' else 'DC 0'
    agg=pwl if kind=='coupling' else 'DC 0'
    text=f'''* Lab 4: {ident}, {kind}. Linear RC model, not a transistor simulation.
.include "../networks/{ident}.spice"
Vsrc SRC 0 {src}
Rsource SRC SIG_DRV {SOURCE_R}
Vagg AGG 0 {agg}
Xroute SIG_DRV SIG_RX AGG 0 ROUTE
Cload SIG_RX 0 {LOAD_C:.12e}
.options reltol=1e-7 abstol=1e-14 vntol=1e-10 method=gear maxord=2
.control
set noaskquit
set wr_singlescale
set wr_vecnames
set numdgt=12
tran {h:.12g} {STOP:.12g} 0 {h:.12g}
wrdata ../raw/{ident}_{kind}.dat v(src) v(sig_drv) {vector(mid,net['node_count'])} v(sig_rx) v(agg)
quit
.endc
.end
'''
    deck=out/'decks'/f'{ident}_{kind}.cir';deck.write_text(text)
    return deck


def run_ngspice(net, kind, out, exe, h):
    ident=net['id']
    deck=write_deck(net,kind,out,h)
    p=subprocess.run([exe,'-b',deck.name],cwd=deck.parent,capture_output=True,text=True,timeout=60)
    log=p.stdout+'\n'+p.stderr
    (out/'logs'/f'{ident}_{kind}.log').write_text(log)
    raw=out/'raw'/f'{ident}_{kind}.dat'
    if p.returncode or not raw.exists() or 'Error:' in log:
        raise RuntimeError(f'ngspice failed: {deck}; see logs/{ident}_{kind}.log')
    rows=[]
    for line in raw.read_text().splitlines()[1:]:
        vals=[float(v) for v in line.split()]
        if len(vals)!=6:raise RuntimeError('Unexpected wrdata column layout: inspect raw file and ngspice version')
        rows.append(vals)
    if not rows or rows[-1][0] < STOP*0.999:
        raise RuntimeError('Transient did not reach its declared stop time')
    return rows


def interp(rows,t,col=4):
    times=[r[0] for r in rows];i=bisect.bisect_left(times,t)
    if i==0:return rows[0][col]
    if i==len(rows):return rows[-1][col]
    a,b=rows[i-1],rows[i];return a[col]+(b[col]-a[col])*(t-a[0])/(b[0]-a[0])


def crossing(rows, level, col):
    for a,b in zip(rows,rows[1:]):
        if a[col]<level<=b[col]:return a[0]+(level-a[col])*(b[0]-a[0])/(b[col]-a[col])
    return None


def measures(step,coupling):
    t_in=crossing(step,VSTEP/2,1);t_out=crossing(step,VSTEP/2,4)
    bad=[i for i,r in enumerate(step) if abs(VSTEP-r[4])>HALF_LSB]
    settled=None
    if bad and bad[-1]<len(step)-1:
        a,b=step[bad[-1]],step[bad[-1]+1]
        ea,eb=abs(VSTEP-a[4]),abs(VSTEP-b[4])
        settled=a[0]+(ea-HALF_LSB)*(b[0]-a[0])/(ea-eb)
    return {'t50_delay_ns':(t_out-t_in)*1e9 if t_in is not None and t_out is not None else None,
            'half_LSB_settling_after_ramp_ns':(settled-(START+RISE))*1e9 if settled is not None else None,
            'output_at_10ns_V':interp(step,10e-9),
            'coupling_peak_mV':max(abs(r[4]) for r in coupling)*1e3,
            'final_step_error_uV':abs(VSTEP-step[-1][4])*1e6}


def write_waveform(out,ident,kind,rows):
    with (out/'waveforms'/f'{ident}_{kind}.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['time_s','source_V','driver_V','midpoint_V','receiver_V','aggressor_V'])
        wr.writerows([[f'{v:.12g}' for v in row] for row in rows])


def svg_text(x,y,s,**kwargs):
    attr=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in kwargs.items())
    return f'<text x="{x}" y="{y}" {attr}>{html.escape(str(s))}</text>'


def layout_svg(g,net,path):
    def xy(p):return 50+p[0],310-p[1]
    def rect(r,color):
        x,y=xy((r[0],r[3]));return f'<rect x="{x}" y="{y}" width="{r[2]-r[0]}" height="{r[3]-r[1]}" fill="{color}" fill-opacity="0.2" stroke="{color}"/>'
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 370" role="img">',
       '<rect width="720" height="370" fill="white"/><g font-family="system-ui,sans-serif" fill="#33414f" font-size="13">',
       rect(g['reference_plane_met2_um'],'#8b9dab')]
    for r in g.get('aggressor_met4_um',[]):s.append(rect(r,'#a56830'))
    for r in g.get('grounded_patch_met4_um',[]):s.append(rect(r,'#168166'))
    points=' '.join(f'{x},{y}' for x,y in map(xy,g['path_um']))
    s.append(f'<polyline points="{points}" fill="none" stroke="#2b6cb0" stroke-width="4" stroke-linejoin="miter"/>')
    for p,label in [(g['path_um'][0],'DRV'),(g['path_um'][-1],'RX')]:
        x,y=xy(p);s.extend([f'<circle cx="{x}" cy="{y}" r="4" fill="#26313c"/>',svg_text(x,y+20,label,text_anchor='middle')])
    s.extend([svg_text(380,45,g['label'],font_weight='700',font_size='18'),
              svg_text(380,79,f"Length: {net['length_um']:g} µm; width: {net['width_um']:g} µm"),
              svg_text(380,105,f"Estimated route R: {net['total_R_ohm']:.3f} Ω"),
              svg_text(380,131,f"C to reference: {net['total_ground_C_fF']:.3f} fF"),
              svg_text(380,157,f"C to aggressor: {net['total_mutual_C_fF']:.3f} fF"),
              svg_text(380,203,'Blue: met3 signal',fill='#2b6cb0'),
              svg_text(380,227,'Orange: met4 aggressor',fill='#a56830'),
              svg_text(380,251,'Green: grounded met4 patch',fill='#168166'),
              svg_text(380,275,'Gray: quiet met2 reference',fill='#5c6b7a'),
              svg_text(360,347,'Positions use µm coordinates; signal stroke is widened for readability.',text_anchor='middle',font_size='12'),
              '</g></svg>'])
    path.write_text('\n'.join(s))


SUP=str.maketrans('-0123456789','⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
def nice_ticks(lo,hi,target=6):
    """Round tick values (1, 2, 2.5 or 5 times a power of ten) covering [lo, hi]."""
    raw=(hi-lo)/max(1,target);mag=10**math.floor(math.log10(raw))
    step=min((m*mag for m in (1,2,2.5,5,10) if m*mag>=raw*0.999),default=10*mag)
    first=math.ceil(lo/step-1e-9)*step
    return [round(first+i*step,12) for i in range(int((hi-first)/step+1e-9)+1)]
def tick_text(v,log=False):
    if log:
        e=round(math.log10(v));return '1' if e==0 else ('10' if e==1 else '10'+str(e).translate(SUP))
    return f'{v:g}'

def plot_svg(path,title,series,ylabel,ymin,ymax,xmax=60,log=False,threshold=None):
    left,right,top,bottom=76,710,58,294
    transform=lambda v:math.log10(max(v,ymin)) if log else v
    lo,hi=transform(ymin),transform(ymax)
    def point(t,v):return left+(right-left)*t/xmax,bottom-(bottom-top)*(transform(v)-lo)/(hi-lo)
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 430" role="img">',
       '<rect width="760" height="430" fill="white"/><g font-family="system-ui,sans-serif" fill="#33414f" font-size="12">',
       svg_text(380,25,title,text_anchor='middle',font_size='17',font_weight='700'),
       svg_text(380,45,'Calculated linear RC network; geometry is an analytical estimate.',text_anchor='middle',font_size='11')]
    for i in range(7):
        t=xmax*i/6;x,_=point(t,ymin)
        s.extend([f'<path d="M{x} {top} V{bottom}" stroke="#e3e9ef"/>',svg_text(x,bottom+18,f'{t:g}',text_anchor='middle')])
    ticks=([10**i for i in range(math.ceil(lo),math.floor(hi)+1)] if log else nice_ticks(ymin,ymax,9))
    for v in ticks:
        _,y=point(0,v);s.extend([f'<path d="M{left} {y} H{right}" stroke="#e3e9ef"/>',svg_text(left-7,y+4,tick_text(v,log),text_anchor='end')])
    s.extend([f'<path d="M{left} {top} V{bottom} H{right}" fill="none" stroke="#8396a8"/>',
              svg_text(394,333,'Time from simulation start (ns)',text_anchor='middle'),
              f'<text x="18" y="180" transform="rotate(-90 18 180)" text-anchor="middle">{html.escape(ylabel)}</text>',
              '<defs><clipPath id="plotclip"><rect x="76" y="58" width="634" height="236"/></clipPath></defs>'])
    for j,(name,data,color) in enumerate(series):
        # Display decimation changes only drawing density, not saved data or metrics.
        stride=max(1,len(data)//1400)
        pts=' '.join(f'{x:.3f},{y:.3f}' for x,y in [point(t,v) for t,v in data[::stride]])
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" clip-path="url(#plotclip)"/>')
        lx=90+(j%2)*330;ly=362+(j//2)*24
        s.extend([f'<path d="M{lx} {ly-4} h24" stroke="{color}" stroke-width="3"/>',svg_text(lx+31,ly,name)])
    if threshold is not None:
        _,y=point(0,threshold);s.extend([f'<path d="M{left} {y} H{right}" stroke="#b33535" stroke-dasharray="5 4"/>',svg_text(right-3,y-6,'12-bit half LSB',text_anchor='end',fill='#b33535')])
    s.append('</g></svg>');path.write_text('\n'.join(s))


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--engine',choices=['auto','ngspice','builtin'],default='auto')
    ap.add_argument('--ngspice',help='Path to ngspice, otherwise NGSPICE or PATH')
    ap.add_argument('--output',default='run_results',help='Output directory, relative to this lab; shipped results/ is preserved by default')
    ap.add_argument('--segment-um',type=float,default=20.0)
    ap.add_argument('--step-ps',type=float,default=10.0)
    a=ap.parse_args()
    if a.segment_um<=0 or a.step_ps<=0 or not all(map(math.isfinite,[a.segment_um,a.step_ps])):ap.error('Segment and step must be positive finite values')
    exe=a.ngspice or os.environ.get('NGSPICE') or shutil.which('ngspice')
    if a.engine=='ngspice' and not exe:ap.error('ngspice requested but not found; supply --ngspice or use --engine builtin')
    engine='ngspice' if exe and a.engine!='builtin' else 'builtin_backward_euler'
    if engine=='ngspice':
        resolved=shutil.which(exe) or str(Path(exe).expanduser().resolve())
        exe=resolved
        version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=10).stdout
        version=next((line.strip('* ') for line in version.splitlines() if 'ngspice-' in line),'ngspice, version unknown')
    else:version='Python standard-library backward Euler, fixed time step'
    out=Path(a.output);out=out if out.is_absolute() else HERE/out
    out.mkdir(parents=True,exist_ok=True)
    for d in ['networks','mapping','waveforms','figures','raw','logs','decks']:(out/d).mkdir(exist_ok=True)
    coeff=json.loads((HERE/'sky130_coefficients.json').read_text())
    geometries=[json.loads(p.read_text()) for p in sorted((HERE/'geometry').glob('*.json'))]
    if not geometries:raise RuntimeError('No input geometry files')
    h=a.step_ps*1e-12
    all_results=[];waves={}
    for g in geometries:
        net=estimate(g,coeff,a.segment_um);write_network(net,out)
        save_json(out/'networks'/f"{net['id']}_estimate.json",net)
        layout_svg(g,net,out/'figures'/f"{net['id']}_layout.svg")
        data={}
        for kind in ['step','coupling']:
            write_deck(net,kind,out,h)
            data[kind]=run_ngspice(net,kind,out,exe,h) if engine=='ngspice' else builtin_transient(net,kind,h)
            write_waveform(out,net['id'],kind,data[kind])
        waves[net['id']]=data
        m=measures(data['step'],data['coupling'])
        all_results.append({k:net[k] for k in ['id','label','length_um','width_um','total_R_ohm','total_ground_C_fF','total_mutual_C_fF','aggressor_overlap_um2','grounded_patch_overlap_um2','node_count']}|m)
        print(f"{net['id']}: R={net['total_R_ohm']:.6g} ohm, Cref={net['total_ground_C_fF']:.6g} fF, Cmutual={net['total_mutual_C_fF']:.6g} fF; delay={m['t50_delay_ns']:.6g} ns, kick={m['coupling_peak_mV']:.6g} mV")
    inputs=[HERE/'run_lab.py',HERE/'sky130_coefficients.json']+sorted((HERE/'geometry').glob('*.json'))
    meta={'model_kind':'analytical geometry-to-RC estimator; not foundry-qualified extraction',
          'simulation_engine':engine,'engine_version':version,'maximum_time_step_ps':a.step_ps,
          'maximum_segment_length_um':a.segment_um,'source_R_ohm':SOURCE_R,'receiver_C_fF':LOAD_C*1e15,
          'stimulus_V':VSTEP,'ramp_start_ns':START*1e9,'ramp_duration_ns':RISE*1e9,'stop_ns':STOP*1e9,
          'half_LSB_V':HALF_LSB,'input_sha256':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
          'limitations':coeff['scope_limitations'],'cases':all_results}
    if 'detour' in waves and 'detour_fill' in waves:
        meta['fill_induced_pair_difference_at_10ns_mV']=(interp(waves['detour']['step'],10e-9)-interp(waves['detour_fill']['step'],10e-9))*1e3
    save_json(out/'summary.json',meta)
    with (out/'summary.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(all_results[0]));wr.writeheader();wr.writerows(all_results)
    normal=[];error=[];coupled=[]
    for j,r in enumerate(all_results):
        name=r['label'];data=waves[r['id']];color=COLORS[j%len(COLORS)]
        normal.append((name,[(q[0]*1e9,q[4]) for q in data['step']],color))
        error.append((name,[(q[0]*1e9,abs(VSTEP-q[4])) for q in data['step']],color))
        coupled.append((name,[(q[0]*1e9,q[4]*1e3) for q in data['coupling']],color))
    plot_svg(out/'figures'/'step_response.svg','Same logical connection, different charging response',normal,'Receiver voltage (V)',0,1.9,xmax=30)
    plot_svg(out/'figures'/'settling_error.svg','The last error band matters',error,'Absolute settling error (V, log scale)',1e-6,2,xmax=60,log=True,threshold=HALF_LSB)
    peak=max(r['coupling_peak_mV'] for r in all_results)
    plot_svg(out/'figures'/'coupling_response.svg','Aggressor transition with the victim source held quiet',coupled,'Receiver disturbance (mV)',0,max(10,peak*1.1),xmax=30)
    print(f'Results written to {out}. Engine: {version}.')

if __name__=='__main__':
    main()
