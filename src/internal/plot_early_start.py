"""Pre-render the appendix comparison; manuscript builds only embed the PDF."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from src import models

ROOT = Path(__file__).resolve().parents[2]
SEEDS = ((2, '#176B87', '-'), (4, '#D55E00', '--'), (5, '#009E73', ':'))
PDF_METADATA = {'CreationDate': None, 'ModDate': None}


def render(destination=None):
    destination = Path(destination) if destination is not None else ROOT/'paper/figures'
    destination.mkdir(parents=True, exist_ok=True)
    z = np.linspace(12, 6, 121)
    shift = models.growth_log10_factor(1, .1, models.cosmic_time_gyr(30)-models.cosmic_time_gyr(3400))
    with plt.rc_context({**plt.rcParamsDefault, 'font.family': 'STIXGeneral',
                         'mathtext.fontset': 'stix', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharex=True, sharey=True)
        fig.subplots_adjust(left=.085, right=.985, bottom=.19, top=.71, wspace=.22)
        for i, (ax, start) in enumerate(zip(axes, (30, 3400))):
            for seed, color, style in SEEDS:
                mass = models.predicted_log_mbh(seed, 1, .1, start, z)
                if start == 3400:
                    np.testing.assert_allclose(mass-models.predicted_log_mbh(seed, 1, .1, 30, z), shift, atol=1e-12)
                ax.plot(z, mass, color=color, linestyle=style, linewidth=1.5)
            ax.set(xlim=(12, 6), ylim=(4, 13.5), xticks=np.arange(6, 13), yticks=np.arange(4, 14, 2))
            ax.grid(alpha=.18)
            ax.set_title(rf'({chr(97+i)}) $z_{{\rm seed}}={start}$', loc='left', pad=15)
            ax.tick_params(labelleft=True)
        axes[0].set_ylabel(r'$\log_{10}(M_{\rm BH}/M_\odot)$')
        fig.supxlabel('Observed redshift', y=.105, fontsize=11)
        fig.text(.5,.96,r'$\epsilon=0.1$, $\overline{f}_{\rm Edd}=1$, $B_{\rm merge}=1$',ha='center')
        handles=[Line2D([],[],color=color,linestyle=style,linewidth=1.5,
                        label=rf'$M_{{\rm seed}}=10^{seed}M_\odot$') for seed,color,style in SEEDS]
        fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.92),ncol=3,frameon=False)
        fig.text(.5,.035,'Earlier onset raises each matched track by 0.868 dex (a factor of 7.37).',ha='center')
        fig.savefig(destination/'early_start_comparison.png',dpi=300,facecolor='white')
        fig.savefig(destination/'early_start_comparison.pdf',facecolor='white',metadata=PDF_METADATA)
        plt.close(fig)


if __name__ == '__main__':
    render()
