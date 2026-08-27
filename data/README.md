# Data Directory Guide

Data products are separated by provenance and release stage.

```text
data/
├── raw/                    source-native and manually curated input tables
├── processed/<release>/    standardized catalogue tables frozen by release
├── crossmatch/<release>/   identity links, aliases, and review decisions
└── registry/               cross-release source and provenance registries
```

Release folder names match their filename prefixes (`v1`, `v3`, `v7_1`, and so
on). Files keep their established names so a table remains recognizable when
downloaded outside the repository.

Earlier processed and crossmatch releases are intentionally retained. A later
catalogue usually extends an earlier one, but the earlier snapshot records the
then-current membership, identity decisions, and schema required to reproduce
its science products. Do not replace an older file with a newer release or
create duplicate aliases at the directory root.

Generated science tables and figures live in `results/releases/<release>/`.
Release hashes and reproduction metadata live in `releases/`.
