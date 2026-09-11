# Catalogue browsing score

This score is used in the atlas interface. Scientific comparisons rank objects by their required average Eddington ratios.


The point navigation score is
$$
S=\min\left[100,100\max\left(C\!\left(\frac{f_2-0.3}{1.2}\right),
C\!\left(\frac{s_{0.3}-4}{2.8}\right)\right)
+8C\!\left(\frac{z-6}{4}\right)\right],
$$
where $C(x)=\min(1,\max(0,x))$, $f_2$ is the required
$f_{\mathrm{Edd}}$ for a $10^2\,M_\odot$ seed, and $s_{0.3}$ is the required
$\log_{10}(M_{\rm seed}/M_\odot)$ at $f_{\mathrm{Edd}}=0.3$. This score combines two growth diagnostics and a redshift term to help
browse the catalogue. It has no probabilistic calibration. Ties use
decreasing $f_2$, decreasing redshift, then stable identifier. The manuscript's required-$f_{\mathrm{Edd}}$ table is ordered directly by $f_2$.
