"""Growth-track layouts, including the adopted manuscript efficiency panels."""
from pathlib import Path
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src import models

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper/figure_options'
COLORS = ['#0072B2', '#D55E00', '#009E73']
SEEDS = [2, 4, 5]
RATES = np.round(np.arange(.1, 2.01, .1), 1)
EPS = [.1, float(models.thin_disk_radiative_efficiency(-1)),
       float(models.thin_disk_radiative_efficiency(0)),
       float(models.thin_disk_radiative_efficiency(1))]


def render(root=ROOT, destination=None):
    from src.internal.publication_figures import load_plot_inputs
    OUT = Path(destination) if destination is not None else root / 'paper/figure_options'
    OUT.mkdir(parents=True, exist_ok=True)
    _, primary_ids, point, *_ = load_plot_inputs(root)
    primary = point[point.physical_object_id.isin(primary_ids)]
    extra = point[~point.physical_object_id.isin(primary_ids)]
    z = np.linspace(3, 11.5, 600)
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

    # For manual selection, comment out the automatic selection block above
    # and remove the first '# ' from each code line below, preserving indentation.
    # manual_tracks = [
    #     (2, EPS[0], 0.5),  # 10^2 solar masses, efficiency 0.1, f_Edd 0.5
    #     (2, EPS[0], 1.0),
    #     (4, EPS[0], 0.3),
    #     (4, EPS[1], 0.2),  # efficiency for spin a = -1
    #     (5, EPS[2], 0.6),  # efficiency for spin a = 0
    #     (5, EPS[3], 1.5),  # efficiency for spin a = +1
    # ]

    # audit['selected_full'] = False
    # for seed, eps, rate in manual_tracks:
    #     mask = (
    #         audit['log_seed'].eq(seed)
    #         & np.isclose(audit['epsilon'], eps)
    #         & np.isclose(audit['rate'], rate)
    #     )
    #     if mask.sum() != 1:
    #         raise ValueError(f"Track not in candidate grid: {(seed, eps, rate)}")
    #     audit.loc[mask, 'selected_full'] = True

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
    plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix', 'font.size':11,
                         'axes.spines.top':False, 'axes.spines.right':False})

    def data(ax, label=False):
        ax.scatter(primary.redshift, primary.log_mbh_msun_std, s=15, color='#69747e',
                   alpha=.4, edgecolors='none', zorder=2, label=f'Primary ({len(primary)})' if label else None)
        ax.scatter(extra.redshift, extra.log_mbh_msun_std, s=30, marker='^', facecolors='none',
                   edgecolors='#733f8c', linewidths=.8, zorder=3,
                   label=f'Exploratory only ({len(extra)})' if label else None)
        ax.set(xlim=(11.5,3), ylim=(5.2,9.6))
        ax.grid(alpha=.12)
    def highlight(ax, names=True, size=8):
        offsets = {
            'GN-z11': (12, -20),
            'CEERS-1019': (-16, -22),
            'GS-20057765': (-16, 13),
            'UNCOVER-20466': (-20, 18),
            'COSMOS3D-13852': (12, 12),
            'RUBIES-EGS-55604': (-12, 6),
        }
        for name, offset in offsets.items():
            obj = point.loc[point.object_id.eq(name)].iloc[0]
            exploratory = obj.physical_object_id not in primary_ids
            color = '#733f8c' if exploratory else '#28333d'
            ax.scatter([obj.redshift], [obj.log_mbh_msun_std], s=35,
                       facecolors='white', edgecolors=color,
                       marker='^' if exploratory else 'o', linewidths=1.1, zorder=6)
            if names:
                ax.annotate(name, (obj.redshift, obj.log_mbh_msun_std),
                            xytext=offset, textcoords='offset points', fontsize=size,
                            ha='right' if offset[0] < 0 else 'left', va='center', color=color,
                            bbox=dict(facecolor='white', edgecolor='none', alpha=.9, pad=1.1),
                            arrowprops=dict(arrowstyle='-', color=color, lw=.6), zorder=7)

    def finish(fig, name, title, subtitle, note):
        fig.suptitle(title, x=.08, ha='left', y=.98, fontsize=17, weight='bold')
        fig.text(.08,.927,subtitle,fontsize=10,color='#444')
        fig.text(.08,.018,note+f'\nGrey circles: primary ({len(primary)}); purple triangles: exploratory only ({len(extra)}).',fontsize=9,color='#444')
        fig.savefig(OUT/f'{name}.png', dpi=220, facecolor='white')
        plt.close(fig)
    note='Data-guided display only: nearby means within 0.5 dex at observed z; not a fit or model probability. All 234 eligible objects shown.'
    fig, axes=plt.subplots(1,3,figsize=(15,5.9),sharex=True,sharey=True)
    fig.subplots_adjust(left=.07,right=.98,bottom=.17,top=.70,wspace=.09)
    for ax,seed,color in zip(axes,SEEDS,COLORS):
        data(ax)
        for (_,rate,count),style in zip([r for r in refs if r[0]==seed],['-', '--', ':']):
            ax.plot(z,models.predicted_log_mbh(seed,rate,.1,30,z),color=color,ls=style,lw=2,
                    label=rf'$\bar f={rate:g}$ ({count} nearby)')
        ax.set_title(rf'$M_{{\rm seed}}=10^{seed}M_\odot$',y=1.25)
        ax.set_xlabel('Observed redshift')
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),fontsize=9,frameon=False,borderaxespad=0)
        highlight(ax, names=seed == SEEDS[0], size=7)
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
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,fontsize=9,ncol=3,borderaxespad=0)
    highlight(ax, size=9)
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
    # Publication layout: shared axis labels and legends outside the data area.
    fig,axes=plt.subplots(2,2,figsize=(13,11),sharex=True,sharey=True)
    fig.subplots_adjust(left=.075,right=.98,bottom=.12,top=.83,hspace=.52,wspace=.13)
    for i, (ax,eps) in enumerate(zip(axes.flat,EPS)):
        data(ax); curves(ax,selected[selected.epsilon.eq(eps)])
        ax.set_title(rf'({chr(97+i)})  $\epsilon={eps:.5f}$',fontsize=12,
                     loc='left', y=1.23)
        ax.legend(title=r'$M_{\mathrm{seed}}$ : $\overline{f}_{\mathrm{Edd}}$',
                  fontsize=9, title_fontsize=9, ncol=3, loc='lower left',
                  bbox_to_anchor=(0,1.01), frameon=False, borderaxespad=0,
                  columnspacing=1.3, handlelength=2.2)
        highlight(ax, names=i == 0, size=8)
        ax.set_xticks(np.arange(3,12))
    fig.supxlabel('Observed redshift',y=.065,fontsize=12)
    fig.supylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$',x=.015,fontsize=12)
    fig.text(.075,.976,'Growth tracks across radiative-efficiency assumptions',
             fontsize=16,weight='bold',va='top')
    fig.text(.075,.938,
             r'$z_{\rm seed}=30$; bands span $B=1$ (thick edge) to $B=2$ (thin edge). '
             'Seed mass is encoded by colour; exact rates are listed above each panel.',fontsize=9)
    fig.text(.075,.025,
             f'Grey circles: primary ({len(primary)}); purple triangles: exploratory only ({len(extra)}). '
             'Outlined targets are named in panel (a).',fontsize=9)
    fig.savefig(OUT/'03_full_efficiency_panels.png',dpi=300,facecolor='white')
    fig.savefig(OUT/'03_full_efficiency_panels.svg',facecolor='white')
    fig.savefig(OUT/'03_full_efficiency_panels.pdf',facecolor='white',
                metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(17,7),sharex=True,sharey=True)
    fig.subplots_adjust(left=.06,right=.98,bottom=.15,top=.68,wspace=.10)
    for ax,seed in zip(axes,SEEDS):
        data(ax); curves(ax,selected[selected.log_seed.eq(seed)],False)
        ax.set_title(rf'$M_{{\rm seed}}=10^{seed}M_\odot$',y=1.32)
        ax.set_xlabel('Observed redshift')
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),fontsize=8,frameon=False,ncol=2,borderaxespad=0)
        highlight(ax, names=seed == SEEDS[0], size=7)
    axes[0].set_ylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$')
    finish(fig,'04_full_seed_panels','D  |  Growth assumptions separated by seed mass',
           'Seed redshift 30. Bands span B = 1 to 2; legends explicitly pair efficiency and average rate.',
           'Same selected scenarios as C. No mass-error fitting; excluded tracks remain documented in track_selection.csv.')

if __name__=='__main__':
    render()
