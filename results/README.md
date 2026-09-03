# Results

`v1/`, `v2/`, and `v3/` have the same complete structure:

```text
results/<version>/
├── figures/               paper-ready summaries and all-object atlases
├── tables/                rankings, follow-up priorities, uncertainty, compatibility, and audits
└── parameter_maps/
    ├── fedd_mass_maps/             f_Edd versus seed-mass panels for every object
    └── seedredshift_mass_maps/     seed-redshift versus seed-mass panels for every object
```

v1 covers all 23 objects numerically; v2 covers all 152 numerically; v3
represents all 174 objects with 153 numerical products and 21 explicit
no-inference panels. Obsolete software-release result trees are not part of the
public repository contract; necessary assembly logic is isolated under
`src/internal/compatibility/`.

Individual growth-track panels are intentionally omitted. A combined
growth-track overview for each version remains under `figures/`. All combined
growth-track figures use the same observed-redshift range from 10 down to 3,
with their existing figure dimensions and plot margins retained. v3 also has
`v3_all_object_growth_tracks_full_assumptions.png`, which preserves the full
historical v1 curve and object-color encodings as a separate companion figure.
