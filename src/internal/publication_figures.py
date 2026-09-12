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

NAMES = ('landscape', 'growth_tracks', 'uncertainty', 'compatibility', 'measurement_sensitivity', 'growth_boundaries')
PRIMARY, SECONDARY = '#0072B2', '#D55E00'


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
    with plt.rc_context({**plt.rcParamsDefault, 'font.family':'STIXGeneral', 'mathtext.fontset':'stix', 'font.size':11, 'axes.labelsize':12, 'axes.titlesize':12,
                         'legend.fontsize':9, 'grid.alpha':.15,
                         'axes.spines.top':False, 'axes.spines.right':False}):
        def save(fig, name):
            fig.savefig(destination/f'{name}.png', dpi=300, facecolor='white')
            fig.savefig(destination/f'{name}.pdf', facecolor='white',
                        metadata={'CreationDate': None, 'ModDate': None})
            plt.close(fig)
        fig, counts = plt.subplots(figsize=(13,5.2))
        fig.subplots_adjust(left=.24,right=.98,bottom=.15,top=.78)
        fig.text(.075,.96,'Manuscript sample accounting',fontsize=16,weight='bold',va='top')
        fig.text(.075,.87,f'{len(selection)} catalogue object records',fontsize=11)
        excluded = selection.excluded_identity_flag
        values = [len(primary),len(point)-len(primary),int((~excluded & ~selection.growth_ranking_eligible_flag).sum()),int(excluded.sum())]
        labels = ['Primary','Exploratory only','Retained without mass','Identity excluded']
        counts.barh(labels,values,color=['#69747e','#874194','#aaa','#444'])
        for i,v in enumerate(values):counts.text(v+2,i,str(v),va='center')
        counts.set(xlabel='Object records',xlim=(0,max(values)*1.18));counts.invert_yaxis()
        counts.grid(axis='x',alpha=.15);counts.set_axisbelow(True)
        save(fig,'landscape')
        # Rebuild the adopted efficiency-panel layout from the same source as option C.
        from src.internal.growth_track_options import render as render_growth_options
        import shutil
        with tempfile.TemporaryDirectory() as growth_tmp, plt.rc_context(plt.rcParamsDefault):
            render_growth_options(root, growth_tmp)
            shutil.copyfile(Path(growth_tmp)/'03_full_efficiency_panels.png',
                            destination/'growth_tracks.png')
            shutil.copyfile(Path(growth_tmp)/'03_full_efficiency_panels.pdf',
                            destination/'growth_tracks.pdf')
        fig,ax=plt.subplots(figsize=(13,7.8))
        fig.subplots_adjust(left=.23,right=.98,bottom=.12,top=.79)
        fig.text(.075,.96,'Objects above the reference growth threshold',fontsize=16,weight='bold',va='top')
        tail_ids = point.loc[point.physical_object_id.isin(primary) & point.required_fedd_seed1e2.gt(1), 'physical_object_id']
        g = uncertainty.loc[uncertainty.physical_object_id.isin(tail_ids)].copy()
        g = g.sort_values('required_fedd_seed1e2_p50',ascending=False)
        offset = build_publication_outputs(root)['mass_offset_object_sensitivity']
        lower = offset.loc[offset.mass_offset_dex.eq(-.5)].set_index('physical_object_id')
        y=np.arange(len(g))
        mid=g.required_fedd_seed1e2_p50.to_numpy()
        ax.errorbar(mid,y,xerr=np.array([mid-g.required_fedd_seed1e2_p16,g.required_fedd_seed1e2_p84-mid]),fmt='o',color=PRIMARY,capsize=3,label='Reported-error median and 16th--84th interval')
        ax.scatter(lower.loc[g.physical_object_id,'required_fedd'],y,marker='D',color=SECONDARY,s=28,label='Point requirement after -0.5 dex mass shift')
        ax.set_yticks(y,g.object_id,fontsize=10);ax.invert_yaxis()
        ax.axvline(1,color='#555',ls='--',lw=1)
        ax.set(xlabel=r'Required $\overline{f}_{\mathrm{Edd,req}}$')
        ax.grid(axis='x',alpha=.15);ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),fontsize=9,frameon=False)
        save(fig,'uncertainty')
        fig,axes=plt.subplots(1,2,figsize=(13,6.5),sharey=True)
        fig.subplots_adjust(left=.085,right=.98,bottom=.14,top=.73,wspace=.15)
        fig.text(.075,.97,'Seed mass and radiative-efficiency constraints',fontsize=16,weight='bold',va='top')
        seeds=np.linspace(1,6,250)
        for name,color,ls in [('UNCOVER-20466',PRIMARY,'-'),('COSMOS3D-13852','#874194','-'),('RUBIES-EGS-55604','#49834c','-'),('GS-20057765','#555555',':'),('GN-z11',SECONDARY,'--')]:
            obj=point.loc[point.object_id.eq(name)].iloc[0]
            for ax,zseed in zip(axes,[30,20]):
                # Solve f_req=1 at fixed seed, start time and B=1 for efficiency.
                a=(models.cosmic_time_gyr(obj.redshift)-models.cosmic_time_gyr(zseed))/(.45*np.log(10)*(obj.log_mbh_msun_std-seeds))
                ax.plot(seeds,a/(1+a),color=color,ls=ls,label=name)
                ax.set(xlabel=r'$\log_{10}(M_{\rm seed}/M_\odot)$',title=rf'({"a" if zseed == 30 else "b"})  $z_{{\rm seed}}={zseed}$',ylim=(.035,.19))
                ax.axhline(.1,color='#aaa',lw=.7);ax.axhline(1-np.sqrt(8/9),color='#aaa',ls=':',lw=.7)
                ax.grid(alpha=.15)
        axes[0].set_ylabel(r'Maximum fixed efficiency for $\overline{f}_{\mathrm{Edd,req}}\leq1$')
        for ax in axes:
            ax.set_title(ax.get_title(),loc='left');ax.set_title('')
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,fontsize=9,frameon=False,loc='upper left',bbox_to_anchor=(.075,.90),ncol=3)
        save(fig,'growth_boundaries')
        seed_names=list(compatibility.seed_model.drop_duplicates())
        fig,axes=plt.subplots(len(seed_names),2,figsize=(13,10),
                              sharex=True,sharey=True,squeeze=False)
        fig.subplots_adjust(left=.09,right=.825,bottom=.14,top=.82,
                            hspace=.48,wspace=.12)
        fig.text(.075,.977,'Compatibility across growth assumptions',fontsize=16,weight='bold',va='top')
        samples = [(primary,f'Primary ({len(primary)})'),
                   (set(point.physical_object_id),f'Exploratory, including primary ({len(point)})')]
        for sample_col,(ids,label) in enumerate(samples):
            position=axes[0,sample_col].get_position()
            fig.text((position.x0+position.x1)/2,.918,label,
                     ha='center',va='center',fontsize=12)
            for seed_row,seed in enumerate(seed_names):
                g=compatibility.loc[compatibility.physical_object_id.isin(ids)&compatibility.seed_model.eq(seed)]
                pivot=g.pivot_table(index='spin_case',columns=['merger_case','f_edd_avg'],values='compatible',aggfunc='mean')
                spin_order=sorted(pivot.index,key=lambda x: 0 if 'minus1' in x else 2 if 'plus1' in x else 1)
                columns=sorted(pivot.columns,key=lambda x: (x[0]=='merger_boost_x2',x[1]))
                pivot=pivot.reindex(index=spin_order,columns=columns)
                ax=axes[seed_row,sample_col]
                im=ax.imshow(pivot.to_numpy(float),vmin=0,vmax=1,cmap='viridis',aspect='auto')
                for y in range(len(pivot)):
                    for x in range(len(pivot.columns)):
                        v=pivot.iloc[y,x]
                        ax.text(x,y,f'{v:.0%}',ha='center',va='center',fontsize=10,
                                color='white' if v<.6 else 'black')
                ax.axvline(2.5,color='white',lw=1.2,alpha=.65)
                ax.set_xticks(range(len(pivot.columns)),[f'{f:g}' for _,f in pivot.columns],fontsize=10)
                ax.set_yticks(range(len(pivot)),['-1' if 'minus1' in x else '+1' if 'plus1' in x else '0' for x in pivot.index],fontsize=10)
                ax.tick_params(axis='x',bottom=seed_row==len(seed_names)-1,
                               labelbottom=seed_row==len(seed_names)-1)
                ax.tick_params(axis='y',left=sample_col==0,labelleft=sample_col==0)
                if seed_row==len(seed_names)-1:
                    for xpos,boost in [(1,1),(4,2)]:
                        ax.text(xpos,-.27,rf'$B_{{\rm merge}}={boost}$',
                                transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=10)
        for seed_row,seed in enumerate(seed_names):
            title = r'$10^2$ to $10^6\,M_\odot$ seed range' if 'pbh' in seed else seed.replace('_',' ').capitalize()
            fig.text(.4575,axes[seed_row,0].get_position().y1+.014,title,
                     ha='center',va='bottom',fontsize=11)
        fig.supylabel(r'Spin, $a$',x=.02,fontsize=12)
        fig.supxlabel(r'Lifetime-average Eddington ratio, $\overline{f}_{\rm Edd}$',
                      y=.025,fontsize=12)
        colorbar=fig.colorbar(im,cax=fig.add_axes([.865,.20,.025,.56]))
        colorbar.set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
        colorbar.set_label('Descriptive compatible fraction',labelpad=10)
        save(fig,'compatibility')
        fig,ax=plt.subplots(figsize=(13,6))
        fig.subplots_adjust(left=.25,right=.98,bottom=.15,top=.77)
        fig.text(.075,.96,'Growth requirements from alternate mass estimates',fontsize=16,weight='bold',va='top')
        labels=[]
        for i,(_,row) in enumerate(sensitivity.iterrows()):
            preferred=row.default_required_fedd_seed1e2;alternate=row.alternate_required_fedd_seed1e2
            ax.plot([preferred,alternate],[i,i],color='#aaa',lw=2)
            ax.scatter(preferred,i,color=PRIMARY,s=35,label='Preferred' if i==0 else None)
            ax.scatter(alternate,i,color=SECONDARY,marker='D',s=30,label='Alternate' if i==0 else None)
            obj=point.loc[point.physical_object_id.eq(row.physical_object_id),'object_id'].iloc[0]
            labels.append(f'{obj} (pair {i+1})')
        ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis()
        ax.axvline(1,color='#555',ls='--',lw=1)
        ax.set(xlabel=r'Required $\overline{f}_{\mathrm{Edd,req}}$',xlim=(0,1.05))
        ax.legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.02),ncol=2);ax.grid(axis='x',alpha=.15)
        save(fig,'measurement_sensitivity')



def verify_figures(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='dayal-publication-figures-') as folder:
        render_figures(root,folder)
        for name in NAMES:
            with Image.open(root/f'paper/figures/{name}.png') as a, Image.open(Path(folder)/f'{name}.png') as b:
                if a.size!=b.size:raise AssertionError(f'{name}: figure dimensions differ')
                if np.abs(np.asarray(a.convert('RGBA')).astype(int)-np.asarray(b.convert('RGBA')).astype(int)).max()>3:
                    raise AssertionError(f'{name}: publication figure pixels differ')
    print(f'Verified {len(NAMES)} publication figures against the conservative sample mask')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify:verify_figures()
    else:render_figures()

if __name__=='__main__':main()
