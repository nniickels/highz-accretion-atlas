"""Render the manuscript's two-object seed-mass/starting-redshift comparison."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.models import required_fedd_for_seed

ROOT = Path(__file__).resolve().parents[2]


def render(destination=None):
    destination = Path(destination) if destination is not None else ROOT/'paper/figures'
    destination.mkdir(parents=True, exist_ok=True)
    objects = pd.read_csv(ROOT/'data/processed/v3/v3_accreting_objects.csv').set_index('object_id')
    seed, start = np.meshgrid(np.linspace(1, 6, 240), np.linspace(11, 30, 240))
    with plt.rc_context({**plt.rcParamsDefault, 'font.family':'STIXGeneral',
                         'mathtext.fontset':'stix', 'font.size':11}):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharex=True, sharey=True)
        fig.subplots_adjust(left=.075, right=.865, bottom=.16, top=.81, wspace=.12)
        for ax, name, group in zip(axes, ['UNCOVER-20466','GN-z11'], ['primary','exploratory']):
            obj = objects.loc[name]
            values = required_fedd_for_seed(seed, float(obj.log_mbh_msun_std), .1,
                                            start, float(obj.redshift), merger_boost=1)
            mesh = ax.pcolormesh(seed, start, values, shading='auto', cmap='magma_r',
                                 vmin=0, vmax=3, rasterized=True)
            contours = ax.contour(seed, start, values, levels=[.3,1,2], colors='white', linewidths=1.2)
            ax.clabel(contours, fmt={.3:'0.3',1:'1',2:'2'}, fontsize=10)
            ax.axvline(2, color='white', linestyle=':', linewidth=.9)
            ax.axhline(20, color='white', linestyle=':', linewidth=.9)
            ax.set(xlim=(1,6), ylim=(11,30), xticks=range(1,7), yticks=[11,15,20,25,30],
                   xlabel=r'$\log_{10}(M_{\rm seed}/M_\odot)$')
            ax.set_title(f'{name} ({group})\n'+rf'$z_{{\rm obs}}={obj.redshift:.3f}$, $\log_{{10}}(M_{{\rm BH}}/M_\odot)={obj.log_mbh_msun_std:.2f}$', fontsize=11)
        axes[0].set_ylabel(r'Starting redshift $z_{\rm seed}$')
        cax=fig.add_axes([.89,.16,.022,.65])
        cb=fig.colorbar(mesh,cax=cax,extend='max',ticks=[0,.3,1,2,3])
        cb.set_label(r'Required average $\overline{f}_{\mathrm{Edd,req}}$')
        fig.savefig(destination/'seed_timing_comparison.pdf', metadata={'CreationDate':None,'ModDate':None},dpi=220)
        fig.savefig(destination/'seed_timing_comparison.png',dpi=220)
        plt.close(fig)


if __name__ == '__main__':
    render()
