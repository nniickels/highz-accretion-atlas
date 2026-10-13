import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/Users/nickel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root=process.cwd();
const result=await finalizePresentation({workspaceDir:root,candidatePath:root+'/.cupc-landscape-build/candidate.pptx',finalPath:root+'/.cupc-landscape-output/checked.pptx',pythonExecutable:'/Users/nickel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:'/Users/nickel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:'/Users/nickel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','43891200,32918400'],explicitTotalSlideCount:2,verifyArtifactToolImport:true,receiptPath:root+'/.cupc-landscape-build/validation-final.json'});
console.log(JSON.stringify(result));
