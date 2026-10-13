"""Package the local manuscript and validate all LaTeX file dependencies."""
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    paper = Path(__file__).resolve().parents[2] / 'paper'
    files = {paper / 'main.tex'}
    pending = list(files)
    while pending:
        source = pending.pop()
        text = re.sub(r'(?<!\\)%[^\n]*', '', source.read_text())
        references = re.findall(
            r'\\(?:includegraphics(?:\[[^\]]*\])?|tableinput|input|include)\{([^}]+)\}', text
        )
        for name in references:
            path = (paper / name).resolve()
            if not path.is_relative_to(paper.resolve()):
                raise ValueError(f'{source.name}: dependency outside paper/: {name}')
            if not path.is_file():
                raise FileNotFoundError(f'{source.name}: missing {name}')
            if path not in files:
                files.add(path)
                if path.suffix == '.tex':
                    pending.append(path)
    output = paper / 'early_giants_overleaf.zip'
    temporary = output.with_suffix('.zip.tmp')
    with ZipFile(temporary, 'w', compression=ZIP_DEFLATED) as archive:
        archive.writestr('README.md',
                         'Upload this ZIP to Overleaf as a new project.\n'
                         'Select main.tex as the main document and pdfLaTeX as the compiler.\n'
                         'The bibliography is embedded; no BibTeX step is needed.\n')
        for path in sorted(files):
            archive.write(path, path.relative_to(paper).as_posix())
    with ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity check failed')
    temporary.replace(output)
    print(f'Created {output.name}: {len(files) + 1} files, {output.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
