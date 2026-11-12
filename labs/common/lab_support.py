"""Small, local-only helpers used by the ASIC teaching labs.

The runners invoke installed tools without a shell and keep logs beside decks.
They never download or install anything. Model hashes are checked before use.
"""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys
import numpy as np
from spice_paths import portable_library_paths

COMMON=Path(__file__).resolve().parent
DEFAULT_MODELS=COMMON/'models/sky130_course.lib.spice'

def verify_models():
    root=COMMON/'models'; manifest=json.loads((root/'source_manifest.json').read_text())
    for item in manifest['files']:
        p=root/'upstream'/item['path']
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=item['sha256']:raise RuntimeError('Model hash mismatch: '+str(p))
    return manifest

def executable(value,env_name,default):
    candidate=value or os.environ.get(env_name) or default
    found=shutil.which(candidate)
    if not found and Path(candidate).is_file():found=str(Path(candidate).resolve())
    if not found:raise RuntimeError(f'{default} was not found. Install it or pass its path; see labs/README.txt.')
    return str(Path(found).resolve())

def run_spice(engine,folder,deck):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    deck=portable_library_paths(deck,folder)
    (folder/'bench.spice').write_text(deck)
    env=os.environ.copy();env['OMP_NUM_THREADS']='1'
    p=subprocess.run([engine,'-b','bench.spice'],cwd=folder,capture_output=True,text=True,timeout=120,env=env)
    log=p.stdout+'\n'+p.stderr;(folder/'ngspice.log').write_text(log)
    if p.returncode or 'fatal error' in log.lower() or 'error:' in log.lower():
        raise RuntimeError(f'ngspice failed in {folder}. Read ngspice.log.\n'+log[-2000:])
    return log

def data(path):
    values=np.loadtxt(path,skiprows=1)
    if values.ndim!=2 or not np.isfinite(values).all():raise RuntimeError('Invalid data: '+str(path))
    return values

def crossing(t,y,level,rising=True,after=0):
    mask=(t[:-1]>=after)&((y[:-1]<level)&(y[1:]>=level) if rising else (y[:-1]>level)&(y[1:]<=level))
    inds=np.flatnonzero(mask)
    if not len(inds):raise RuntimeError('Required crossing absent: check settling, polarity and simulation duration.')
    k=inds[0]
    return float(t[k]+(level-y[k])*(t[k+1]-t[k])/(y[k+1]-y[k]))

def relative_spice(path,folder):
    return os.path.relpath(Path(path).resolve(),Path(folder).resolve()).replace(os.sep,'/')

def metadata(engine,models,kind):
    ver=subprocess.run([engine,'--version'],capture_output=True,text=True).stdout
    bundled=Path(models).resolve()==DEFAULT_MODELS.resolve()
    m=verify_models() if bundled else {'revision':'external model file supplied by the runner caller'}
    return {'kind':kind,'tool':ver.strip(),'python':sys.version.split()[0],
      'numpy':np.__version__,'models_revision':m['revision'],
      'model_wrapper_sha256':hashlib.sha256(Path(models).read_bytes()).hexdigest(),
      'conditions':'Deterministic corner simulations; mismatch switches disabled in bundled upstream files. No silicon or signoff result.'}

def plot_style():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#26313c','text.color':'#26313c','svg.fonttype':'none','axes.prop_cycle':plt.cycler(color=['#2468a0','#bb6f33','#45846b','#8b5a9d'])})
    return plt
