# hla2010-spec Source Root Migration

## Current State

- installable package root: `packages/hla2010-spec/`
- historical source root: `src/hla2010/`
- repo-internal tooling root: `src/hla2010_repo_internal/`

## Target State

- installable package root: `packages/hla2010-spec/`
- package-owned source root: `packages/hla2010-spec/src/hla2010/`
- repo-internal tooling root remains: `src/hla2010_repo_internal/`

## Affected Imports

- runtime namespace stays the same: `import hla2010`
- clean spec front door stays the same: `from hla2010.spec import ...`
- temporary compatibility facade stays the same: `from hla2010.rti import ...`

This migration changes file ownership and source-root layout, not the public
import surface.

## Affected Tests

- pytest source-checkout `pythonpath` must include `packages/hla2010-spec/src`
- runtime adapter and namespace-policy tests must read `packages/hla2010-spec/src/hla2010/*`
- doc-policy tests must treat `packages/hla2010-spec/src/hla2010/` as the canonical spec source root
- traceability and compliance artifacts must point to `packages/hla2010-spec/src/hla2010/*`

## Artifact Impact

- generated compliance artifacts that cited `src/hla2010/*` need regeneration
- generated traceability artifacts that cited `src/hla2010/*` need regeneration
- operator checks that validate repo layout must point at `packages/hla2010-spec/src/hla2010/`

## Rollback Plan

1. Move `packages/hla2010-spec/src/hla2010/` back to `src/hla2010/`.
2. Restore root `pyproject.toml` pytest `pythonpath` ordering.
3. Restore `packages/hla2010-spec/pyproject.toml` package discovery to `../../src`.
4. Regenerate compliance and traceability artifacts from the restored layout.
5. Re-run `./tools/human-editability check` and the package-boundary test suites.
