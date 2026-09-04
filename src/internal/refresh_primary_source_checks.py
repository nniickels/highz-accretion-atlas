"""Refresh the independent four-paper fixture from primary HTML downloads.

Requires BeautifulSoup from the pinned notebook environment. Run only after
reviewing the primary sources; this is not part of catalogue generation.
"""

import argparse
import re,json,hashlib
from pathlib import Path
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html_directory', type=Path, help='Directory with cosmos.html, nexus.html, jades.html, seven.html')
    args = parser.parse_args()
    BASE = args.html_directory
    checks=[]; sources=[]
    def triple(s):
     s=s.replace('−','-')
     if not re.search(r'\d',s):return None,None,None
     v=float(re.search(r'[+-]?\d+(?:\.\d+)?',s).group())
     p=re.search(r'\\pm\s*([\d.]+)|±\s*([\d.]+)',s)
     if p:return v,float(p.group(1) or p.group(2)),float(p.group(1) or p.group(2))
     p=re.search(r'\^\{\+([\d.]+)\}',s);m=re.search(r'_\{-([\d.]+)\}',s)
     return v,float(p.group(1)) if p else None,float(m.group(1)) if m else None
    
    def rows(name,key,url):
     path=BASE/(name+'.html');s=BeautifulSoup(path.read_text(),'html.parser')
     for m in s.select('math'):m.replace_with(m.get('alttext',''))
     table=next(t for t in s.select('table') if key in t.get_text())
     rr=[[c.get_text(' ',strip=True) for c in r.find_all(['td','th'],recursive=False)] for r in table.select('tr')]
     sources.append(dict(id=name,url=url,retrieved='2026-09-04',retrieved_html_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),table_cells=rr))
     return rr
    
    def add(source,path,key_col,key,col,val,cell):
     checks.append(dict(source=source,path=path,key_column=key_col,key=key,column=col,expected=val,source_cell=cell))
    
    for name,key,url in [('cosmos','13852','https://arxiv.org/html/2504.08039v2'),('nexus','NX21958','https://arxiv.org/html/2505.20393v1')]:
     rr=rows(name,key,url)
     path='data/raw/'+('lin25_cosmos3d_blagn_table1.csv' if name=='cosmos' else 'zhuang25_nexus_wfss_table1_zge4.csv')
     for r in rr:
      if name=='cosmos':
       if not re.match(r'^\d',r[0]):continue
       obj='COSMOS3D-'+re.search(r'\d+',r[0]).group()
       specs=[(1,'ra_deg',None,None),(2,'dec_deg',None,None),(3,'redshift',None,None),(4,'f444w_mag','f444w_err','f444w_err'),(5,'broad_fwhm_km_s','broad_fwhm_err_plus','broad_fwhm_err_minus'),(6,'line_luminosity_1e42','line_luminosity_err_plus','line_luminosity_err_minus'),(7,'log_mbh_msun','log_mbh_err_plus','log_mbh_err_minus'),(8,'muv','muv_err_plus','muv_err_minus'),(9,'beta_opt','beta_opt_err','beta_opt_err')]
      else:
       if not r[0].startswith('NX') or float(r[3])<4:continue
       obj=r[0]
       specs=[(1,'ra_deg',None,None),(2,'dec_deg',None,None),(3,'redshift',None,None),(4,'f444w_mag','f444w_err','f444w_err'),(5,'log_line_luminosity','log_line_luminosity_err_plus','log_line_luminosity_err_minus'),(7,'broad_fwhm_km_s','broad_fwhm_err_plus','broad_fwhm_err_minus'),(9,'log_mbh_msun','log_mbh_err_plus','log_mbh_err_minus')]
      for i,v,p,m in specs:
       for col,value in zip([v,p,m],triple(r[i])):
        if col:add(name,path,'object_id',obj,col,value,r[i])
      if name=='cosmos':add(name,path,'object_id',obj,'muv_censoring','lower_limit' if '>' in r[8] else 'detection',r[8])
      add(name,path,'object_id',obj,'broad_line_species','Hbeta' if name=='cosmos' and '13852' in obj else ('Halpha' if name=='cosmos' or triple(r[9])[0] is not None else None),'Table 1 line column / note')
      # Independently check that the source mass reaches canonical fields with its errors.
      mass_i=7 if name=='cosmos' else 9
      for col,value in zip(['log_mbh_msun_std','log_mbh_err_plus_std','log_mbh_err_minus_std'],triple(r[mass_i])):
       add(name,'data/processed/v3/v3_accreting_measurements.csv','object_id',obj,col,value,r[mass_i])
    rr=rows('jades','20057765','https://arxiv.org/html/2504.03551v2')
    for r in rr:
     if not re.match(r'^(GN|GS)-',r[0]) or float(r[3]) < 4:continue
     # Select the source measurement rather than same-object alternates.
     for i,col,plus,minus in [(1,'ra_deg',None,None),(2,'dec_deg',None,None),(3,'redshift',None,None),(4,'log_mbh_msun_std','log_mbh_err_plus_std','log_mbh_err_minus_std'),(5,'log_lbol_erg_s_std','log_lbol_err_plus_std','log_lbol_err_minus_std'),(6,'edd_ratio_std',None,None)]:
      for f,v in zip([col,plus,minus],triple(r[i])):
       if f:
        add('jades','data/processed/v1/v1_accreting_measurements.csv','object_id',r[0],f,v,r[i])
    rr=rows('seven','GHZ7','https://arxiv.org/html/2410.10967v1')
    for r in rr:
     if r[0] not in ['GHZ4','GHZ7']:continue
     for i,col,plus,minus in [(1,'ra_deg',None,None),(2,'dec_deg',None,None),(3,'redshift','redshift_err_plus','redshift_err_minus'),(4,'lensing_mu',None,None),(6,'muv','muv_err_plus','muv_err_minus'),(7,'beta_uv','beta_uv_err','beta_uv_err')]:
      for f,v in zip([col,plus,minus],triple(r[i])):
       if f:add('seven','data/raw/napolitano25_seven_wonders_agn_candidates.csv','object_id',r[0],f,v,r[i])
    out=Path(__file__).resolve().parents[2] / 'data/validation';out.mkdir(exist_ok=True)
    (out/'primary_source_checks.json').write_text(json.dumps({'scope':'Independent re-read of COSMOS-3D Table 1, NEXUS Table 1 z>=4, JADES BH table z>=4, and Seven Wonders GHZ4/GHZ7 rows; not an exhaustive audit of all 32 families.','sources':sources,'checks':checks},indent=2)+'\n')
    print(len(checks),'source-cell checks')


if __name__ == "__main__":
    main()
