#!/usr/bin/env python3
"""Run the included ASIC teaching labs with installed tools and local references."""
from pathlib import Path
import argparse,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--labs',nargs='+',choices=['1','2','3','4','5','analysis'],default=['1','2','3','4','5','analysis'])
    p.add_argument('--ngspice');p.add_argument('--iverilog');p.add_argument('--vvp')
    p.add_argument('--include-synthesis',action='store_true');p.add_argument('--yosys');p.add_argument('--abc')
    args=p.parse_args()
    paths={'1':'L01_inverter/run.py','2':'L02_bias_amplifier/run_lab.py','3':'L03_sampling_interface/run.py','4':'L04_layout_extraction/run_lab.py','5':'L05_mixed_signal_integration/run.py','analysis':'analysis_examples/run.py'}
    commands=[]
    for lab in args.labs:
        cmd=[sys.executable,str(HERE/paths[lab])]
        if lab in ['1','2','3','4'] and args.ngspice:cmd+=['--ngspice',str(Path(args.ngspice).expanduser().resolve())]
        if lab=='4' and args.ngspice:cmd+=['--engine','ngspice']
        if lab=='5':
            if args.iverilog:cmd+=['--iverilog',str(Path(args.iverilog).expanduser().resolve())]
            if args.vvp:cmd+=['--vvp',str(Path(args.vvp).expanduser().resolve())]
        commands.append((lab,cmd))
    if args.include_synthesis:
        cmd=[sys.executable,str(HERE/'L05_mixed_signal_integration/synthesis_example/run_synthesis.py')]
        if args.yosys:cmd+=['--yosys',str(Path(args.yosys).expanduser().resolve())]
        if args.abc:cmd+=['--abc',str(Path(args.abc).expanduser().resolve())]
        commands.append(('synthesis',cmd))
    report=[]
    for lab,cmd in commands:
        print('\nRunning '+lab+': '+str(Path(cmd[1]).relative_to(HERE)),flush=True)
        start=time.monotonic()
        result=subprocess.run(cmd,cwd=HERE.parent,check=False)
        report.append({'lab':lab,'returncode':result.returncode,'elapsed_seconds':round(time.monotonic()-start,3)})
        (HERE/'run_report.json').write_text(json.dumps(report,indent=2))
        if result.returncode:
            print('Stopped after a failed lab. Inspect its log and the setup guide.',file=sys.stderr);return result.returncode
    print('\nAll requested lab runners completed. New results are separate from the supplied results/ snapshots.')
    return 0
if __name__=='__main__':raise SystemExit(main())

