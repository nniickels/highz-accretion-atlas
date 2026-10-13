import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('.cupc-landscape-build/candidate.pptx'));
const slide=p.slides.items[1];
// Author the landscape placements, retaining the source OOXML package for math fidelity.
const heading=slide.shapes.items.find(s=>s.name==='Efficiency comparison heading');
heading.position={left:16.65*96,top:23.35*96,width:14.35*96,height:.7*96};
await (await PresentationFile.exportPptx(p)).save('.cupc-landscape-build/authored.pptx');
console.log('Landscape imported and authored with native text and images.');
