# Release Manifest Guide

This directory contains machine-readable release contracts. A manifest records
the release scope, expected counts, exact artifact membership, and SHA-256
hashes. It is metadata, not a second copy of the released data.

## Current v7.5 contracts

- `v7.5-catalogue-manifest.json`: catalogue, identity, host, and observable products
- `v7.5-science-manifest.json`: class-aware rankings, summaries, and exclusions
- `v7.5-figures-manifest.json`: four paper figures and inherited-gallery coverage
- `v7.5-publication-manifest.json`: manuscript and publication documentation
- `source-provenance-manifest.json`: cross-source provenance supplement

## Frozen contracts

Files beginning with `v4.0.1` through `v7.4` describe immutable historical
releases. Their corresponding verification commands are listed in
[`../docs/getting-started.md`](../docs/getting-started.md) and run in CI.

Do not edit an old artifact merely to make it resemble the current release.
Corrections belong in a new release with a new manifest.

