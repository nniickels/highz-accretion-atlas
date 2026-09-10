"""Review-only growth-track layouts; explicitly data-guided, not fitted histories."""
from pathlib import Path
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src import models
from src.internal.publication_figures import load_plot_inputs

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper/figure_options'
COLORS = ['#0072B2', '#D55E00', '#009E73']
SEEDS = [2, 4, 5]
RATES = np.round(np.arange(.1, 2.01, .1), 1)
EPS = [.1, float(models.thin_disk_radiative_efficiency(-1)),
       float(models.thin_disk_radiative_efficiency(0)),
       float(models.thin_disk_radiative_efficiency(1))]


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    _, primary_ids, point, *_ = load_plot_inputs()
    primary = point[point.physical_object_id.isin(primary_ids)]
    extra = point[~point.physical_object_id.isin(primary_ids)]
    z = np.linspace(4, 11.5, 500)
    rows = []
    for seed, eps, rate in product(SEEDS, EPS, RATES):
        # Count a nearby prediction for either displayed boost, at each object's z.
        distances = [abs(models.predicted_log_mbh(seed, rate, eps, 30,
                     primary.redshift.to_numpy(), merger_boost=b)
                     - primary.log_mbh_msun_std.to_numpy()) for b in [1, 2]]
        near = np.minimum(*distances)
        rows.append(dict(log_seed=seed, epsilon=eps, rate=rate,
                         nearby_primary=int((near <= .5).sum()),
                         median_distance_dex=float(np.median(near))))
    audit = pd.DataFrame(rows)
    audit['selected_full'] = False
    for _, g in audit.groupby(['log_seed', 'epsilon']):
        selected = g[g.nearby_primary.ge(5)].sort_values(
            ['nearby_primary', 'median_distance_dex', 'rate'], ascending=[False, True, True]).head(2)
        audit.loc[selected.index, 'selected_full'] = True
    audit.to_csv(OUT/'track_selection.csv', index=False, float_format='%.8g')
    # Reference options use B=1, so select independently on that precise history.
    refs = []
    for seed in SEEDS:
        options = []
        for rate in RATES:
            distance = abs(models.predicted_log_mbh(seed, rate, .1, 30,
                           primary.redshift.to_numpy()) - primary.log_mbh_msun_std.to_numpy())
            options.append((int((distance <= .5).sum()), float(np.median(distance)), rate))
        best = sorted(options, key=lambda x: (-x[0], x[1], x[2]))[:3]
        refs.extend((seed, rate, count) for count, _, rate in best if count >= 5)
    pd.DataFrame(refs, columns=['log_seed','rate','nearby_primary']).to_csv(OUT/'reference_selection.csv', index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11,
                         'axes.spines.top':False, 'axes.spines.right':False})

    def data(ax, label=False):
        ax.scatter(primary.redshift, primary.log_mbh_msun_std, s=15, color='#69747e',
                   alpha=.4, edgecolors='none', zorder=2, label='Primary (224)' if label else None)
        ax.scatter(extra.redshift, extra.log_mbh_msun_std, s=30, marker='^', facecolors='none',
                   edgecolors='#733f8c', linewidths=.8, zorder=3,
                   label='Exploratory only (10)' if label else None)
        ax.set(xlim=(11.5,4), ylim=(5.2,9.6))
        ax.grid(alpha=.12)
    def finish(fig, name, title, subtitle, note):
        fig.suptitle(title, x=.08, ha='left', y=.98, fontsize=17, weight='bold')
        fig.text(.08,.927,subtitle,fontsize=10,color='#444')
        fig.text(.08,.018,note+'\nGrey circles: primary (224); purple triangles: exploratory only (10).',fontsize=9,color='#444')
        fig.savefig(OUT/f'{name}.png', dpi=220, facecolor='white')
        plt.close(fig)
    note='Data-guided display only: nearby means within 0.5 dex at observed z; not a fit or model probability. All 234 eligible objects shown.'
    fig, axes=plt.subplots(1,3,figsize=(15,5.9),sharex=True,sharey=True)
    fig.subplots_adjust(left=.07,right=.98,bottom=.17,top=.79,wspace=.09)
    for ax,seed,color in zip(axes,SEEDS,COLORS):
        data(ax)
        for (_,rate,count),style in zip([r for r in refs if r[0]==seed],['-', '--', ':']):
            ax.plot(z,models.predicted_log_mbh(seed,rate,.1,30,z),color=color,ls=style,lw=2,
                    label=rf'$\bar f={rate:g}$ ({count} nearby)')
        ax.set_title(rf'$M_{{\rm seed}}=10^{seed}M_\odot$',pad=12)
        ax.set_xlabel('Observed redshift')
        ax.legend(loc='upper left',fontsize=9,frameon=True,facecolor='white')
    axes[0].set_ylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$')
    finish(fig,'01_reference_seed_panels','A  |  Reference tracks separated by seed mass',
           'Fixed efficiency 0.1; seed redshift 30; B = 1. Three most nearby rates per seed from 0.1–2.0 (step 0.1).', note)
    fig,ax=plt.subplots(figsize=(11,7))
    fig.subplots_adjust(left=.10,right=.97,bottom=.17,top=.79)
    data(ax,label=True)
    for seed,color in zip(SEEDS,COLORS):
        _,rate,count=next(r for r in refs if r[0]==seed)
        ax.plot(z,models.predicted_log_mbh(seed,rate,.1,30,z),color=color,lw=2.2,
                label=rf'$10^{seed}M_\odot$, $\bar f={rate:g}$ ({count} nearby)')
    ax.set(xlabel='Observed redshift',ylabel=r'$\log_{10}(M_{\rm BH}/M_\odot)$')
    ax.legend(loc='upper left',frameon=True,fontsize=10)
    finish(fig,'02_reference_minimal','B  |  Three representative reference tracks',
           'Fixed efficiency 0.1; seed redshift 30; B = 1. Most nearby candidate rate per seed.',
           'Selection is illustrative, dominated by the sample at z ≈ 4–6; curves are not fitted evolutionary histories.')
    selected=audit[audit.selected_full]
    def curves(ax, g, color_by_seed=True):
        for i, row in enumerate(g.itertuples()):
            color=COLORS[SEEDS.index(row.log_seed)] if color_by_seed else plt.get_cmap('tab10')(i)
            lo=models.predicted_log_mbh(row.log_seed,row.rate,row.epsilon,30,z)
            hi=lo+np.log10(2)
            ax.fill_between(z,lo,hi,color=color,alpha=.08)
            style='-' if i%2==0 else '--'
            ax.plot(z,lo,color=color,ls=style,lw=1.6)
            ax.plot(z,hi,color=color,ls=style,lw=.7,alpha=.7)
            label=rf'$10^{{{row.log_seed}}}M_\odot$: {row.rate:g}' if color_by_seed else rf'$\epsilon={row.epsilon:.3f},\ \bar f={row.rate:g}$'
            ax.plot([],[],color=color,ls=style,lw=2,label=label)
    fig,axes=plt.subplots(2,2,figsize=(13,10),sharex=True,sharey=True)
    fig.subplots_adjust(left=.08,right=.98,bottom=.13,top=.84,hspace=.24,wspace=.12)
    for ax,eps in zip(axes.flat,EPS):
        data(ax); curves(ax,selected[selected.epsilon.eq(eps)])
        ax.set_title(rf'Fixed $\epsilon={eps:.5f}$',fontsize=12)
        ax.legend(title=r'Seed mass: $\bar f$',fontsize=8,ncol=2,loc='upper left',framealpha=.95)
    for ax in axes[-1]:ax.set_xlabel('Observed redshift')
    for ax in axes[:,0]:ax.set_ylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$')
    finish(fig,'03_full_efficiency_panels','C  |  Growth assumptions separated by efficiency',
           'Seed redshift 30. Bands span B = 1 (thick lower edge) to 2 (thin upper edge); two nearby rates per seed and efficiency.',
           'Rates selected from 0.1–2.0 by proximity; ≥5 primary objects within 0.5 dex of either boost required. Not a physical fit.')
    fig,axes=plt.subplots(1,3,figsize=(17,7),sharex=True,sharey=True)
    fig.subplots_adjust(left=.06,right=.98,bottom=.15,top=.79,wspace=.10)
    for ax,seed in zip(axes,SEEDS):
        data(ax); curves(ax,selected[selected.log_seed.eq(seed)],False)
        ax.set_title(rf'$M_{{\rm seed}}=10^{seed}M_\odot$')
        ax.set_xlabel('Observed redshift')
        ax.legend(loc='upper left',fontsize=8,framealpha=.95)
    axes[0].set_ylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$')
    finish(fig,'04_full_seed_panels','D  |  Growth assumptions separated by seed mass',
           'Seed redshift 30. Bands span B = 1 to 2; legends explicitly pair efficiency and average rate.',
           'Same selected scenarios as C. No mass-error fitting; excluded tracks remain documented in track_selection.csv.')

if __name__=='__main__':
    render()
