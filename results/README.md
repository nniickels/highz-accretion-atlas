# Results

`v1/`, `v2/`, and `v3/` have the same complete structure:

```text
results/<version>/
├── figures/               paper-ready summaries and all-object atlases
├── tables/                rankings, follow-up priorities, uncertainty, compatibility, and audits
└── gallery/per_object/    parameter, growth-track, and seed-redshift panels for every object
```

v1 covers all 23 objects numerically; v2 covers all 112 numerically; v3
represents all 219 objects with 196 numerical products and 23 explicit
no-inference panels. Obsolete software-release result trees are not part of the
public repository contract; necessary assembly logic is isolated under
`src/internal/compatibility/`.
