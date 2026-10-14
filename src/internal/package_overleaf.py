"""Package the local draft or verify its public PDF and Overleaf snapshot."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PDF_NAME = 'early_giants_draft.pdf'
ZIP_NAME = 'early_giants_overleaf.zip'
MANIFEST = 'MANIFEST.json'
GUIDE = ('Upload this ZIP to Overleaf as a new project.\n'
         'Select main.tex as the main document and pdfLaTeX as the compiler.\n'
         'The bibliography is embedded; no BibTeX step is needed.\n'
         'The public draft PDF is available alongside this ZIP in the repository.\n'
         'MANIFEST.json records source hashes and the matching draft PDF hash.\n')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_dependencies(read):
    """Collect only the main source and recursively referenced figures/tables."""
    files, pending = {'main.tex'}, ['main.tex']
    while pending:
        name = pending.pop()
        text = re.sub(r'(?<!\\)%[^\n]*', '', read(name).decode())
        for dependency in re.findall(
                r'\\(?:includegraphics(?:\[[^\]]*\])?|tableinput|input|include)\{([^}]+)\}', text):
            path = PurePosixPath(dependency)
            allowed = (not path.is_absolute() and '..' not in path.parts
                       and path.as_posix() == dependency and len(path.parts) == 2
                       and ((path.parts[0] == 'figures' and path.suffix == '.pdf')
                            or (path.parts[0] == 'tables' and path.suffix == '.tex')))
            if not allowed:
                raise ValueError(f'Private or unsupported manuscript dependency: {dependency}')
            read(dependency)  # Fail on a missing dependency before publication.
            if dependency not in files:
                files.add(dependency)
                if path.suffix == '.tex':
                    pending.append(dependency)
    return files


def verify_section_order(source, pdf):
    text = re.sub(r'(?<!\\)%[^\n]*', '', source)
    bib = text.index(r'\begin{thebibliography}')
    end = text.index(r'\end{thebibliography}') + len(r'\end{thebibliography}')
    appendix = text.index(r'\appendix')
    if not bib < end < appendix:
        raise ValueError('References must precede appendices')
    if not text[:bib].rstrip().endswith(r'\clearpage'):
        raise ValueError('References must start on a new page')
    if text[end:appendix].strip() != r'\clearpage':
        raise ValueError('Appendices must start on a new page')
    pages = [page.extract_text() or '' for page in PdfReader(pdf).pages]
    refs = [i for i, page in enumerate(pages) if re.search(r'^References\s*$', page, re.M)]
    apps = [i for i, page in enumerate(pages) if re.search(r'^Appendix\s+A\b', page, re.M)]
    if len(refs) != 1 or len(apps) != 1 or refs[0] >= apps[0]:
        raise ValueError('PDF references/appendix order differs from source')
    for i, heading in [(refs[0], 'References'), (apps[0], 'Appendix A')]:
        if not pages[i].lstrip().startswith(heading):
            raise ValueError(f'PDF {heading} must begin on a new page')
    return {'references_page': refs[0] + 1, 'appendix_page': apps[0] + 1}


def verify_public(root=ROOT):
    paper = Path(root) / 'paper'
    pdf = paper / PDF_NAME
    with ZipFile(paper / ZIP_NAME) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise ValueError('Invalid or duplicate ZIP entries')
        manifest = json.loads(archive.read(MANIFEST))
        sources = source_dependencies(archive.read)
        expected = sources | {'README.md', MANIFEST}
        if set(names) != expected or set(manifest['files_sha256']) != expected - {MANIFEST}:
            raise ValueError('Manuscript package membership differs; private or missing files')
        if manifest['format_version'] != 1:
            raise ValueError('Unsupported manuscript manifest')
        for name, digest in manifest['files_sha256'].items():
            if sha256(archive.read(name)) != digest:
                raise ValueError(f'Manuscript source hash differs: {name}')
        if sha256(pdf.read_bytes()) != manifest['pdf_sha256']:
            raise ValueError('Draft PDF hash differs from manuscript package')
        sections = verify_section_order(archive.read('main.tex').decode(), pdf)
    return {'manuscript_verification': 'pass', 'source_files': len(sources), **sections}


def package(root=ROOT):
    paper = Path(root) / 'paper'
    read = lambda name: (paper / name).read_bytes()
    files = {name: read(name) for name in source_dependencies(read)}
    verify_section_order(files['main.tex'].decode(), paper / PDF_NAME)
    files['README.md'] = GUIDE.encode()
    manifest = {'format_version': 1,
                'files_sha256': {name: sha256(data) for name, data in sorted(files.items())},
                'pdf_sha256': sha256((paper / PDF_NAME).read_bytes())}
    files[MANIFEST] = (json.dumps(manifest, indent=2) + '\n').encode()
    output = paper / ZIP_NAME
    temporary = output.with_suffix('.zip.tmp')
    with ZipFile(temporary, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    with ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity check failed')
    temporary.replace(output)
    return verify_public(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Read-only public snapshot verification')
    args = parser.parse_args()
    print(json.dumps(verify_public() if args.verify else package(), indent=2))


if __name__ == '__main__':
    main()
