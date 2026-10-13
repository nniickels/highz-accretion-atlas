from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import copy,hashlib
b=Path('.cupc-landscape-build');N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'};U=914400
with ZipFile(b/'source-horizontal.pptx') as z:d={n:z.read(n) for n in z.namelist()}
with ZipFile(b/'source-portrait.pptx') as z:s={n:z.read(n) for n in z.namelist()}
r=E.fromstring(s['ppt/slides/slide1.xml']);old=E.fromstring(d['ppt/slides/slide2.xml'])
pos={32:(0,0,48,4.8),33:(.8,.6,3.1,3.1),36:(3.6,1.15,6.6,2.381),37:(43.6,.5,3.4,3.4),
69:(1,5.6,14.75,1.05),70:(1.5,7,13.75,3.55),71:(1,5.6,14.75,5.1),
72:(1,11.25,14.75,1.05),73:(1.5,12.65,13.75,15.7),74:(1,11.25,14.75,17.6),
81:(1,29.4,14.75,1.05),82:(1.5,30.8,13.75,4.05),83:(1,29.4,14.75,5.85),
7:(16.35,5.6,30.65,1.05),11:(16.35,5.6,30.65,17.2),2:(16.85,7,14,6.0),
4:(16.5,13.15,14.8,8.51),110:(16.85,21.7,14.0,1.0),
76:(32.5,7.0,14.0,2.2),14:(32.1,9.4,14.8,9.99),112:(32.5,19.5,14,.55),15:(32.5,20.25,14,1.65),
78:(32,23.35,15,1.05),79:(32.5,24.75,14,9.85),80:(32,23.35,15,11.9),
120:(16.65,23.35,14.35,.7),3:(16.6,24.25,14.5,10.106),111:(16.65,34.4,14.35,.85)}
# Preserve each figure's original aspect ratio exactly.
for el in r.findall('.//p:sp',N)+r.findall('.//p:pic',N):
 id=int(el.find('.//p:cNvPr',N).get('id'));xf=el.find('p:spPr/a:xfrm',N)
 if id in (5,6,10):
  previous=next(e for e in old.findall('.//p:pic',N) if int(e.find('.//p:cNvPr',N).get('id'))==id)
  xf.getparent().replace(xf,copy.deepcopy(previous.find('p:spPr/a:xfrm',N)))
  if id in (5,6):
   off=el.find('p:spPr/a:xfrm/a:off',N);off.set('y',str(int(off.get('y'))-round(.8*U)))
  continue
 if id not in pos:continue
 x,y,w,h=pos[id]
 if E.QName(el).localname=='pic':
  ext=xf.find('a:ext',N);ratio=int(ext.get('cx'))/int(ext.get('cy'));h=w/ratio
 for node,key,value in [('a:off','x',x),('a:off','y',y),('a:ext','cx',w),('a:ext','cy',h)]:xf.find(node,N).set(key,str(round(value*U)))
 if id==32:
  bp=el.find('p:txBody/a:bodyPr',N);bp.set('lIns',str(round(10.3*U)));bp.set('rIns',str(round(13.0*U)));bp.set('tIns',str(round(.1*U)))
  for t in el.findall('.//a:t',N):t.text=t.text.replace('Growth\nConstraints','Growth Constraints')
# Copy slide-2-only media; retain the untouched first slide's assets and relationships.
rels=E.fromstring(s['ppt/slides/_rels/slide1.xml.rels'])
for rel in rels:
 target=rel.get('Target');kind=rel.get('Type').split('/')[-1]
 if kind=='image':
  oldkey='ppt/'+target.removeprefix('../');name='landscape_current_'+Path(oldkey).name;d['ppt/media/'+name]=s[oldkey];rel.set('Target','../media/'+name)
 elif kind=='notesSlide':rel.set('Target','../notesSlides/notesSlide2.xml')
d['ppt/slides/slide2.xml']=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
d['ppt/slides/_rels/slide2.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
d['ppt/notesSlides/notesSlide2.xml']=s['ppt/notesSlides/notesSlide1.xml']
# Existing theme/layout identities are shared; verify content rather than silently substituting styles.
for key in ['ppt/theme/theme1.xml']:
 assert E.tostring(E.fromstring(d[key]),method='c14n')==E.tostring(E.fromstring(s[key]),method='c14n'),key
with ZipFile(b/'candidate.pptx','w',ZIP_DEFLATED) as z:
 for n,v in d.items():z.writestr(n,v)
(b/'source-horizontal.sha256').write_text(hashlib.sha256((b/'source-horizontal.pptx').read_bytes()).hexdigest())
(b/'source-portrait.sha256').write_text(hashlib.sha256((b/'source-portrait.pptx').read_bytes()).hexdigest())
print('Current portrait content copied into landscape slide 2; slide 1 preserved.')
