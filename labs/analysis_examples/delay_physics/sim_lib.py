"""Shared helpers for the delay-physics examples (lesson 27 and lesson 34)."""
from pathlib import Path
import sys, json
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'common'))
from lab_support import DEFAULT_MODELS, verify_models, executable, run_spice, data, crossing, relative_spice  # noqa: E402

def inv_subckt(n):
    """inv_n built as n parallel copies of the two inv_1 devices (0.65 um NMOS, 1.0 um HVT PMOS, L 0.15 um).
    Lesson 11 shows that sky130_fd_sc_hd__inv_1/2/4 use exactly this parallel-device scheme. No layout parasitics."""
    lines = [f'.subckt inv{n} A VGND VNB VPB VPWR Y']
    for k in range(n):
        lines.append(f'XN{k} Y A VGND VNB sky130_fd_pr__nfet_01v8 w=0.65 l=0.15')
        lines.append(f'XP{k} Y A VPWR VPB sky130_fd_pr__pfet_01v8_hvt w=1.0 l=0.15')
    lines.append('.ends')
    return '\n'.join(lines)

def header(models, folder, corner='tt', temp=25):
    return (f'.lib "{relative_spice(models, folder)}" {corner}\n.temp {temp}\n'
            '.options reltol=1e-5 abstol=1e-14 vntol=1e-8\n' + '\n'.join(inv_subckt(n) for n in (1, 2, 4, 8, 16)) + '\n')
