# Backend Route Inventory: Baselines

This page explains the named CERTI baselines and how to compare them.

The backend names do not change between upstream and patched CERTI. The
baseline is selected by environment:

- `certi-patched`
  - `HLA2010_CERTI_PATCHED_PREFIX`
  - `HLA2010_CERTI_PATCHED_BUILD_ROOT`
  - or the repo-local default `HLA2010_CERTI_PREFIX` / `HLA2010_CERTI_BUILD_ROOT`
- `certi-upstream`
  - `HLA2010_CERTI_UPSTREAM_PREFIX`
  - `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`

Primary compare command:

```bash
./tools/certi-easy smoke compare
```

Use this page when the question is:

- is this behavior a generic CERTI limitation?
- or did the local patched CERTI branch change it?

Use this page when you need attribution across CERTI baselines.
