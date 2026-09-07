"""Render manuscript figures from the explicit conservative publication mask."""
from __future__ import annotations
import argparse
from pathlib import Path
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from src import models
from src.internal.publication_selection import ROOT, build_publication_outputs

NAMES = ('landscape', 'growth_tracks', 'uncertainty', 'compatibility', 'measurement_sensitivity')
PRIMARY, SECONDARY = '#176B87', '#B66A1E'


def load_plot_inputs(root=ROOT):
    selection = build_publication_outputs(root)['publication_object_selection']
    primary = set(selection.loc[selection.publication_primary_flag, 'physical_object_id'])
    exploratory = set(selection.loc[selection.publication_exploratory_flag, 'physical_object_id'])
    tables = root/'results/v3/tables'
    def selected(name):
        frame = pd.read_csv(tables/f'v3_{name}.csv')
        return frame.loc[frame.physical_object_id.isin(exploratory)].copy()
    # Notebook 02 precedes atlas-table generation: derive compatibility from
    # the current objects rather than a potentially stale notebook-03 product.
    from src.internal.atlas import build_object_compatibility
    objects = pd.read_csv(root/'data/processed/v3/v3_accreting_objects.csv')
    compatibility = build_object_compatibility(objects.loc[objects.physical_object_id.isin(exploratory)])
    return selection, primary, selected('object_point_ranking'), selected('object_uncertainty_ranking'), compatibility, selected('alternate_measurement_sensitivity')


def render_figures(root=ROOT, destination=None):
    destination = Path(destination) if destination is not None else root/'paper/figures'
    destination.mkdir(parents=True, exist_ok=True)
    selection, primary, point, uncertainty, compatibility, sensitivity = load_plot_inputs(root)
    groups = [(point.physical_object_id.isin(primary), 'Primary', PRIMARY, 'o'),
              (~point.physical_object_id.isin(primary), 'Exploratory only', SECONDARY, '^')]
    with plt.rc_context({**plt.rcParamsDefault, 'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False, 'axes.spines.right':False}):
        def save(fig, name):
            fig.savefig(destination/f'{name}.png', dpi=300, facecolor='white')
            plt.close(fig)
        def masses(ax):
            for mask, label, color, marker in groups:
                g = point.loc[mask]
                ax.scatter(g.redshift, g.log_mbh_msun_std, s=24, alpha=.8,
                           color=color, marker=marker, edgecolor='white', linewidth=.3,
                           label=f'{label} ({len(g)})')
            ax.set(xlabel='Observed redshift', ylabel=r'$\log_{10}(M_{\rm BH}/M_\odot)$')
            ax.grid(alpha=.15)
        fig, (ax, counts) = plt.subplots(1,2,figsize=(10.5,4.5), constrained_layout=True, gridspec_kw={'width_ratios':[1.4,1]})
        masses(ax);ax.legend(frameon=False);ax.set_title('Manuscript numerical samples')
        excluded = selection.excluded_identity_flag
        values = [len(primary),len(point)-len(primary),int((~excluded & ~selection.growth_ranking_eligible_flag).sum()),int(excluded.sum())]
        labels = ['Primary','Exploratory only','Retained without mass','Identity excluded']
        counts.barh(labels,values,color=[PRIMARY,SECONDARY,'#aaa','#666'])
        for i,v in enumerate(values):counts.text(v+2,i,str(v),va='center')
        counts.set(xlabel='Object records',xlim=(0,max(values)*1.18),title=f'Catalogue accounting ({len(selection)})');counts.invert_yaxis()
        save(fig,'landscape')
        fig,ax=plt.subplots(figsize=(10.5,5.5),constrained_layout=True)
        z=np.linspace(3,13,300)
        for seed,color in [(2,'#6688aa'),(4,'#719874'),(6,'#aa7777')]:
            for rate,ls in [(.3,'--'),(1,'-')]:
                ax.plot(z,models.predicted_log_mbh(seed,rate,.1,30,z),color=color,ls=ls,lw=1,
                        label=rf'$M_{{\rm seed}}=10^{seed}M_\odot$, $\bar f={rate:g}$')
        masses(ax);ax.set(xlim=(13,3),ylim=(4.5,10.8),title='Growth tracks and publication samples')
        ax.legend(ncol=3,fontsize=8,frameon=False);save(fig,'growth_tracks')
        fig,ax=plt.subplots(figsize=(10.5,5.2),constrained_layout=True)
        point_only=uncertainty.mbh_uncertainty_mode.eq('point_estimate_no_reported_mbh_error')
        for is_primary,label,color,marker in [(True,'Primary',PRIMARY,'o'),(False,'Exploratory only',SECONDARY,'^')]:
            g=uncertainty.loc[uncertainty.physical_object_id.isin(primary).eq(is_primary)&~point_only]
            width=g.required_fedd_seed1e2_p84-g.required_fedd_seed1e2_p16
            ax.scatter(g.required_fedd_seed1e2_p50,g.prob_required_fedd_seed1e2_gt_1,s=22+80*np.clip(width,0,1),color=color,marker=marker,alpha=.75,label=f'{label}, reported errors ({len(g)})')
        g=uncertainty.loc[point_only]
        ax.scatter(g.required_fedd_seed1e2_p50,np.full(len(g),-.1),marker='D',facecolors='none',edgecolors=PRIMARY,label=f'Primary, no reported errors ({len(g)})')
        ax.set_yticks([-.1,0,.25,.5,.75,1],['No error','0','0.25','0.50','0.75','1'])
        ax.axvline(1,color='#777',ls='--',lw=1);ax.axhline(-.05,color='#aaa',ls=':',lw=.7)
        ax.set(xlabel=r'Median required $\bar f_{\rm Edd}$ ($10^2M_\odot$ seed)',ylabel=r'Conditional $P(\bar f_{\rm Edd,req}>1)$',title=f'Publication uncertainty: {len(uncertainty)-len(g)} sampled, {len(g)} point-only')
        ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=9);save(fig,'uncertainty')
        seed_names=list(compatibility.seed_model.drop_duplicates())
        fig,axes=plt.subplots(2,len(seed_names),figsize=(12,6),constrained_layout=True,squeeze=False)
        for row,(ids,label) in enumerate([(primary,f'Primary ({len(primary)})'),(set(point.physical_object_id),f'Exploratory incl. primary ({len(point)})')]):
            for col,seed in enumerate(seed_names):
                g=compatibility.loc[compatibility.physical_object_id.isin(ids)&compatibility.seed_model.eq(seed)]
                pivot=g.pivot_table(index='spin_case',columns=['merger_case','f_edd_avg'],values='compatible',aggfunc='mean')
                spin_order=sorted(pivot.index,key=lambda x: 0 if 'minus1' in x else 2 if 'plus1' in x else 1)
                columns=sorted(pivot.columns,key=lambda x: (x[0]=='merger_boost_x2',x[1]))
                pivot=pivot.reindex(index=spin_order,columns=columns)
                ax=axes[row,col];im=ax.imshow(pivot.to_numpy(float),vmin=0,vmax=1,cmap='viridis',aspect='auto')
                for y in range(len(pivot)):
                    for x in range(len(pivot.columns)):
                        v=pivot.iloc[y,x];ax.text(x,y,f'{v:.0%}',ha='center',va='center',fontsize=7,color='white' if v<.6 else 'black')
                ax.set_title('PBH-labelled mass range' if 'pbh' in seed else seed.replace('_',' ').capitalize(),fontsize=10)
                ax.set_xticks(range(len(pivot.columns)),[f'B={2 if b=="merger_boost_x2" else 1}\nf={f:g}' for b,f in pivot.columns],fontsize=7)
                ax.set_yticks(range(len(pivot)),['a=-1' if 'minus1' in x else 'a=+1' if 'plus1' in x else 'a=0' for x in pivot.index],fontsize=9)
                if col==0:ax.set_ylabel(label)
        fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.85,label='Descriptive compatible fraction')
        fig.suptitle('Compatibility by publication sample (not population frequencies)')
        save(fig,'compatibility')
        fig,ax=plt.subplots(figsize=(10.5,4.8),constrained_layout=True)
        labels=[]
        for i,(_,row) in enumerate(sensitivity.iterrows(),1):
            x=row.delta_log_mbh_alternate_minus_default;y=row.delta_required_fedd_alternate_minus_default
            ax.scatter(x,y,color=PRIMARY,s=35);ax.annotate(str(i),(x,y),xytext=(5,4),textcoords='offset points',fontsize=8)
            labels.append(f'{i}. {row.alternate_measurement_id}')
        ax.axhline(0,color='#aaa',lw=.7);ax.axvline(0,color='#aaa',lw=.7)
        ax.set(xlabel=r'Alternate minus preferred $\log_{10}M_{\rm BH}$ (dex)',ylabel=r'Alternate minus preferred required $\bar f_{\rm Edd}$',title=f'Publication measurement sensitivity: {len(sensitivity)} pairs, {sensitivity.physical_object_id.nunique()} objects')
        ax.text(1.02,.98,'\n'.join(labels),transform=ax.transAxes,va='top',fontsize=8)
        ax.grid(alpha=.15);save(fig,'measurement_sensitivity')


def verify_figures(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='dayal-publication-figures-') as folder:
        render_figures(root,folder)
        for name in NAMES:
            with Image.open(root/f'paper/figures/{name}.png') as a, Image.open(Path(folder)/f'{name}.png') as b:
                if a.size!=b.size:raise AssertionError(f'{name}: figure dimensions differ')
                if np.abs(np.asarray(a.convert('RGBA')).astype(int)-np.asarray(b.convert('RGBA')).astype(int)).max()>3:
                    raise AssertionError(f'{name}: publication figure pixels differ')
    print('Verified five publication figures against the conservative sample mask')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify:verify_figures()
    else:render_figures()

if __name__=='__main__':main()
