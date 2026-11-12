#!/usr/bin/env python3
"""Reproduce the synthetic trim and FFT examples in lessons 49 and 50.

These calculations use assumed signals and trim steps, not a SKY130 device model.
No network access, external simulator, or PDK installation is needed.
"""
from pathlib import Path
import argparse, csv, json, sys
import numpy as np
from scipy.signal import periodogram
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'common'))
from lab_support import plot_style

def power_bins(x):
    """Single-sided mean-square voltage by bin, even-length real record."""
    n=len(x)
    if n%2:raise ValueError('This teaching helper expects an even record length.')
    p=np.abs(np.fft.rfft(x))**2/n**2
    p[1:-1]*=2
    return p

def alias_bin(k,n):
    b=k%n
    return min(b,n-b)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'run_results')
    args=ap.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    plt=plot_style()
    offsets=np.linspace(-2200,2200,4401)
    # Round half upward here, then clip. Ties are documented; they do not affect |e| bound.
    codes=np.clip(np.floor(32-offsets/50+.5),0,63).astype(int)
    correction=(codes-32)*50
    residual=offsets+correction
    with (out/'trim_sweep.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['offset_uV','code','correction_uV','residual_uV'])
        w.writerows(zip(offsets,codes,correction,residual))
    inrange=(offsets>=-1550)&(offsets<=1600)
    assert np.max(np.abs(residual[inrange]))<=25+1e-10
    sample_offset=1260.;sample_code=int(np.clip(np.floor(32-sample_offset/50+.5),0,63))
    trim={'assumptions':'Ideal monotonic 6-bit trim; 50 uV step; neutral code 32; no noise or mismatch',
          'correction_range_uV':[-1600,1550],'covered_offset_span_uV':[-1550,1600],
          'sample_offset_uV':sample_offset,'sample_code':sample_code,'sample_residual_uV':sample_offset+(sample_code-32)*50,
          'maximum_abs_inrange_quantization_residual_uV':float(np.max(np.abs(residual[inrange]))),
          'two_point_voltage_at_code2065_V':.2+(2065-470)*(1.6-.2)/(3660-470),
          'two_point_slope_mV_per_code':1000*(1.6-.2)/(3660-470)}
    fig,axes=plt.subplots(2,1,figsize=(8.5,6.2),sharex=True)
    axes[0].plot(offsets,codes);axes[0].set(ylabel='Selected code',title='Ideal 6-bit trim: range and step are separate limits')
    axes[1].plot(offsets,residual);axes[1].axhline(25,color='#777',ls=':');axes[1].axhline(-25,color='#777',ls=':');axes[1].set(xlabel='Untrimmed offset (µV)',ylabel='Residual offset (µV)')
    for ax in axes:
        ax.axvspan(-1550,1600,alpha=.08,color='#45846b');ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'trim_range.svg');plt.close(fig)
    temp=np.linspace(-40,125,331)
    # Illustrative curvature after correcting offset and linear term at endpoints.
    raw=1000+8*(temp-25)+.08*(temp-25)**2
    line=np.interp(temp,[-40,125],[raw[0],raw[-1]])
    corrected=raw-line
    fig,ax=plt.subplots(figsize=(8.5,4.3));ax.plot(temp,raw,label='Assumed initial error');ax.plot(temp,corrected,label='After endpoint linear correction');ax.axhline(0,color='#777',lw=1);ax.scatter([-40,125],[0,0],color='#bb6f33');ax.set(xlabel='Temperature (°C)',ylabel='Error (µV)',title='Two endpoint measurements do not remove curvature');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'trim_temperature.svg');plt.close(fig)
    trim['temperature_example']='e(T)=1000+8(T−25)+0.08(T−25)^2 uV, linear endpoint correction at −40 and125 C; not PDK data'
    trim['remaining_curvature_min_uV']=float(corrected.min())

    n=4096;fs=1e6;k=67;amp=.8;span=1.8;seed=20261106
    t=np.arange(n)/fs;f0=k*fs/n;rng=np.random.default_rng(seed)
    analog=.9+amp*np.sin(2*np.pi*f0*t)+.0008*np.sin(4*np.pi*f0*t+.3)+.0004*np.sin(6*np.pi*f0*t+.6)+rng.normal(0,200e-6,n)
    q=span/2**14;codes_adc=np.clip(np.floor(analog/q),0,2**14-1).astype(int)
    volts=(codes_adc+.5)*q;ac=volts-volts.mean();p=power_bins(ac)
    harmonics=sorted({alias_bin(k*h,n) for h in range(2,6)}-{0,k})
    signal=float(p[k]);hd=float(p[harmonics].sum());noise_mask=np.ones(len(p),bool);noise_mask[[0,k]+harmonics]=False
    pn=float(p[noise_mask].sum());sinad=10*np.log10(signal/(pn+hd));snr=10*np.log10(signal/pn)
    spur_mask=np.ones(len(p),bool);spur_mask[[0,k]]=False;spur=float(p[spur_mask].max());spurbin=int(np.flatnonzero(spur_mask)[np.argmax(p[spur_mask])])
    fft={'signal_origin':'Synthetic numerical example, not a fabricated ADC or SKY130 transistor simulation','seed':seed,'N':n,'fs_Hz':fs,'fundamental_bin':k,'fin_Hz':f0,'df_Hz':fs/n,'input_peak_V':amp,'full_scale_span_V':span,'quantizer_bits':14,'assumed_noise_rms_uV':200,'harmonic_bins_h2_to_h5':harmonics,
         'SNR_dB':float(snr),'SINAD_dB':float(sinad),'THD_dBc':float(10*np.log10(hd/signal)),'SFDR_dBc':float(10*np.log10(signal/spur)),'largest_spur_bin':spurbin,
         'signal_dBFS':float(10*np.log10(signal/((span/2)**2/2))),'SINAD_equivalent_bits_at_test_amplitude':float((sinad-1.76)/6.02),'measured_noise_rms_uV':float(np.sqrt(pn)*1e6),'measured_signal_rms_V':float(np.sqrt(signal))}
    # Independent normalization and Parseval checks catch common FFT scaling errors.
    f_sci,psd_sci=periodogram(ac,fs=fs,window='boxcar',detrend=False,scaling='density')
    np.testing.assert_allclose(p,psd_sci*(fs/n),rtol=1e-11,atol=1e-18)
    np.testing.assert_allclose(p.sum(),np.mean(ac**2),rtol=1e-12)
    pure=amp*np.sin(2*np.pi*k*np.arange(n)/n)
    np.testing.assert_allclose(power_bins(pure)[k],amp**2/2,rtol=1e-12)
    with (out/'adc_record.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['sample','time_s','raw_code','reconstructed_V']);w.writerows(zip(range(n),t,codes_adc,volts))
    frequencies=np.fft.rfftfreq(n,1/fs)
    with (out/'spectrum.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['frequency_Hz','mean_square_V2_per_bin']);w.writerows(zip(frequencies,p))
    fig,ax=plt.subplots(figsize=(8.5,4.7));ax.plot(frequencies/1000,10*np.log10(np.maximum(p,1e-25)/(.9**2/2)),lw=.7);ax.scatter(frequencies[[k]+harmonics]/1000,10*np.log10(p[[k]+harmonics]/(.9**2/2)),s=20,color='#bb6f33');ax.set(xlabel='Frequency (kHz)',ylabel='Bin power (dBFS)',ylim=(-135,5),title='Coherent synthetic record: fundamental, distortion and noise');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'fft_coherent.svg');plt.close(fig)
    hann=.5-.5*np.cos(2*np.pi*np.arange(n)/n);cg=float(hann.mean());enbw=float(n*np.sum(hann**2)/np.sum(hann)**2)
    np.testing.assert_allclose([cg,enbw],[.5,1.5],rtol=1e-12)
    noncoherent=amp*np.sin(2*np.pi*(k+.35)*np.arange(n)/n)
    fig,ax=plt.subplots(figsize=(8.5,4.7))
    for win,name in [(np.ones(n),'Rectangular'),(hann,'Periodic Hann')]:
        amplitude=2*np.abs(np.fft.rfft(noncoherent*win))/np.sum(win)
        ax.plot(np.arange(len(amplitude)),20*np.log10(np.maximum(amplitude/amp,1e-15)),label=name)
    ax.set(xlim=(40,95),ylim=(-100,5),xlabel='FFT bin number',ylabel='Amplitude relative to input (dB)',title='67.35 cycles: window reduces leakage, widens the main lobe');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'fft_window.svg');plt.close(fig)
    fft['periodic_Hann']={'coherent_gain':cg,'ENBW_bins':enbw,'ENBW_Hz':enbw*fs/n}
    noise_rows=[];fig,ax=plt.subplots(figsize=(8.5,4.5))
    for count in [4096,16384]:
        noise=np.random.default_rng(seed+count).normal(0,200e-6,count);noise-=noise.mean();pp=power_bins(noise);ff=np.fft.rfftfreq(count,1/fs)
        # Plot smooth, non-overlapping 32-bin mean powers; raw arrays remain regenerable.
        groups=(len(pp)-1)//32;avg=pp[1:1+groups*32].reshape(-1,32).mean(axis=1);ff_avg=ff[1:1+groups*32].reshape(-1,32).mean(axis=1)
        ax.plot(ff_avg/1000,10*np.log10(avg/(.9**2/2)),label=f'N={count:,}; 32-bin means')
        noise_rows.append({'N':count,'df_Hz':fs/count,'integrated_rms_uV':float(np.sqrt(pp.sum())*1e6),'mean_nonedge_bin_power_dBFS':float(10*np.log10(pp[1:-1].mean()/(.9**2/2)))})
    ax.set(xlabel='Frequency (kHz)',ylabel='Mean bin power (dBFS)',title='More samples lower noise per bin; total noise stays about 200 µV RMS');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'fft_noise_bins.svg');plt.close(fig)
    fft['noise_length_comparison']=noise_rows
    summary={'trim':trim,'fft':fft,'checks':['Trim residual within half a step inside stated correction range','FFT bin-power sum equals time-domain mean square','FFT bin powers agree with independent scipy.signal.periodogram density × bin width','Pure coherent sine has A²/2 power','Periodic Hann coherent gain=0.5 and ENBW=1.5 bins'], 'python':sys.version.split()[0],'numpy':np.__version__}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
