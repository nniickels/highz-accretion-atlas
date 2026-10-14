"""Rebuild the scientific plot assets used in the editable CUPC posters."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
from src import models

import argparse
import hashlib
import json
import os
from src.internal.reproduction import assert_csv_reproduction


def verify_inputs(*, baseline_root=None):
    manifest=json.loads((ROOT/'data/poster_inputs.json').read_text())
    baseline_root = baseline_root or os.environ.get('HIGHZ_BASELINE_ROOT')
    for name, expected in manifest['sha256'].items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if actual == expected:
            continue
        if Path(name).suffix != '.csv' or not baseline_root:
            raise ValueError(f'Poster input changed: {name}. Review the poster claims before updating data/poster_inputs.json.')
        baseline = Path(baseline_root).resolve()
        if baseline == ROOT.resolve():
            raise ValueError('Poster CSV baseline must be independent of regenerated inputs')
        original = baseline/name
        if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Poster CSV baseline does not match pinned input: {name}')
        # Same comparison contract as the scientific workflow. No hash refresh,
        # new tolerance, skipped input, or comparison of a workspace with itself.
        assert_csv_reproduction(original, pd.read_csv(ROOT/name))


def main():
    parser=argparse.ArgumentParser(description='Render CUPC figures from reviewed scientific tables; never writes canonical results.')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--landscape-uncertainty-only', action='store_true')
    parser.add_argument('--uncertainty-only', action='store_true')
    args=parser.parse_args()
    verify_inputs()
    O=args.output_dir.resolve()
    O.mkdir(parents=True,exist_ok=True)
    font_size=22.2 if args.landscape_uncertainty_only else 24
    plt.rcParams.update({'font.family':'DejaVu Sans','mathtext.fontset':'dejavusans','font.size':font_size,'axes.labelsize':font_size,'axes.titlesize':26,'xtick.labelsize':font_size,'ytick.labelsize':font_size,'axes.titlecolor':'#002A5C','axes.edgecolor':'#737373','axes.linewidth':1.2,'grid.color':'#B0B0B0','grid.linewidth':0.8,'axes.spines.top':False,'axes.spines.right':False})
    def save(f,n):
     for a in f.axes:
      a.tick_params(axis='both',width=1.2,length=5,color='#737373',pad=6)
     f.savefig(O/(n+'.png'),dpi=200,facecolor='white');plt.close(f)
    sel=pd.read_csv(ROOT/'results/for_manuscript/tables/publication_object_selection.csv');primary=set(sel.loc[sel.publication_primary_flag,'physical_object_id']);expanded=set(sel.loc[sel.publication_exploratory_flag,'physical_object_id'])
    pt=pd.read_csv(ROOT/'results/v3/tables/v3_object_point_ranking.csv');pt=pt[pt.physical_object_id.isin(expanded)]
    un=pd.read_csv(ROOT/'results/v3/tables/v3_object_uncertainty_ranking.csv');tail=set(pt.loc[pt.physical_object_id.isin(primary)&pt.required_fedd_seed1e2.gt(1),'physical_object_id']);g=un[un.physical_object_id.isin(tail)].sort_values('required_fedd_seed1e2_p50',ascending=False)
    off=pd.read_csv(ROOT/'results/for_manuscript/tables/mass_offset_object_sensitivity.csv');off=off[off.mass_offset_dex.eq(-.5)].set_index('physical_object_id')
    f,a=plt.subplots(figsize=(14.8,7.6) if args.landscape_uncertainty_only else (16,8.6));f.subplots_adjust(left=.35,right=.98,bottom=.15 if args.landscape_uncertainty_only else .12,top=.83)
    y=np.arange(len(g));mid=g.required_fedd_seed1e2_p50.to_numpy();a.errorbar(mid,y,xerr=[mid-g.required_fedd_seed1e2_p16,g.required_fedd_seed1e2_p84-mid],fmt='o',color='#0072B2',capsize=5,ms=8,lw=2,label='Median from mass-error draws (16th–84th percentiles)');a.scatter(off.loc[g.physical_object_id,'required_fedd'],y,marker='D',s=75,color='#D55E00',label='Required ratio after −0.5 dex mass shift');a.set_yticks(y,g.object_id);a.invert_yaxis();a.axvline(1,color='#737373',ls='--',lw=1.5);a.set_xlabel(r'Required average Eddington ratio, $\overline{f}_{\rm Edd,req}$');a.grid(axis='x',alpha=.18)
    f.legend(*a.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.11,.98),frameon=False,fontsize=font_size)
    save(f,'uncertainty')
    if args.landscape_uncertainty_only or args.uncertainty_only:
     return
    # Hold all assumptions except efficiency fixed; use the exact repository growth law.
    f,axes=plt.subplots(2,1,figsize=(16.5,11.5),sharex=True,sharey=True);f.subplots_adjust(left=.11,right=.98,bottom=.16,top=.83,hspace=.38)
    z=np.linspace(3,11.5,600);colors=['#0072B2','#D55E00','#009E73']
    for a,eps,title in zip(axes,[.1,float(models.thin_disk_radiative_efficiency(0))],[r'Reference: $\epsilon=0.1$',r'Non-spinning thin disc: $\epsilon=0.05719$']):
     for subset,marker,color in [(pt[pt.physical_object_id.isin(primary)],'o','#59636d'),(pt[~pt.physical_object_id.isin(primary)],'^','#733f8c')]:a.scatter(subset.redshift,subset.log_mbh_msun_std,s=28,marker=marker,color=color,alpha=.85,zorder=4)
     for seed,color in zip([2,4,5],colors):a.plot(z,models.predicted_log_mbh(seed,1,eps,30,z),color=color,lw=2.5,label=rf'$10^{seed}\,M_\odot$ seed')
     a.set(xlim=(11.5,3),ylim=(5.2,9.6),yticks=[6,7,8,9]);a.set_title(title,loc='left',pad=12);a.grid(alpha=.18)
    axes[1].set_xlabel('Observed redshift');f.supylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$',x=.01,fontsize=font_size)
    f.legend(*axes[0].get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.10,.98),frameon=False,ncol=3,fontsize=font_size)
    f.text(.11,.895,r'Same $z_{\rm seed}=30$, average ratio $=1$, no mergers',fontsize=font_size)
    f.text(.11,.045,'Grey circles: primary (220); purple triangles: expanded only (14).',fontsize=font_size)
    save(f,'growth')
    # Same precomputed onset grid, caps, percentiles and cosmology as v4.
    t=pd.read_csv(ROOT/'results/v4/tables/v4_minimum_seed_mass.csv');targets=['UNCOVER-20466','COSMOS3D-13852','RUBIES-EGS-55604','GN-z11'];f,axes=plt.subplots(2,2,figsize=(16,10.8),sharex=True,sharey=True);f.subplots_adjust(left=.09,right=.98,bottom=.20,top=.75,hspace=.42,wspace=.14)
    for a,oid in zip(axes.flat,targets):
     s=t[(t.object_id==oid)&t.mass_offset_dex.eq(0)]
     for cap,col in zip([.3,1,2],['#0072B2','#D55E00','#009E73']):
      p=s[np.isclose(s.epsilon,.1)&np.isclose(s.fedd_cap,cap)];a.plot(p.z_accretion,p.log10_minimum_seed_central,color=col,lw=2.5,label=rf'$f_{{\rm cap}}={cap:g},\ \epsilon=0.1$');a.fill_between(p.z_accretion,p.log10_minimum_seed_p16,p.log10_minimum_seed_p84,color=col,alpha=.14)
     p=s[np.isclose(s.epsilon,models.thin_disk_radiative_efficiency(0))&np.isclose(s.fedd_cap,1)];a.plot(p.z_accretion,p.log10_minimum_seed_central,'--',color='#737373',lw=2.5,label=r'$f_{\rm cap}=1,\ \epsilon=0.05719$')
     a.axvline(30,color='#A0A0A0',ls=':',lw=1.5);a.axhline(2,color='#A0A0A0',ls=':',lw=1.5);a.axhline(5,color='#A0A0A0',ls=':',lw=1.5);a.set_xscale('log');a.set_yticks([0,2,4,6]);a.set_title(oid,loc='left',pad=10);a.grid(alpha=.18)
    f.legend(*axes.flat[0].get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.09,.985),ncol=2,frameon=False,fontsize=font_size)
    f.text(.09,.80,r'$f_{\rm cap}$: assumed maximum average Eddington ratio; no mergers',fontsize=font_size)
    f.supxlabel(r'Accretion-onset redshift, $z_{\rm acc}$ (earlier to the right)',y=.105,fontsize=font_size);f.supylabel(r'Minimum $\log_{10}(M_{\rm seed}/M_\odot)$',x=.005,fontsize=font_size)
    f.text(.09,.068,'Shaded bands: 16th–84th percentiles from mass-error draws.',fontsize=font_size);f.text(.09,.025,r'Dotted lines: $z_{\rm acc}=30$; $M_{\rm seed}=10^2,10^5\,M_\odot$.',fontsize=font_size)
    save(f,'onset')
    print('Poster figures generated from the existing catalogue and numerical tables.')

if __name__ == '__main__':
    main()
