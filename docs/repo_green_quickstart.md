# Repo Green Quickstart

Use this page when the question is:

"How do I get this repo green without reading half the docs tree?"

This is the shortest junior-friendly path.

## One-Page Summary

From the repo root:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/python verify
```

If that passes, the repo is green on the normal local lane.

If it fails, do not rerun everything immediately. Narrow it:

```bash
./tools/test-surface recommend
./tools/test-focus inventory
./tools/test-focus run <target>
./tools/test tests/path/to_file.py
./tools/test tests/path/to_file.py::test_name
```

## The Default Path

Run these in order:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/python verify
```

What they mean:

- `./tools/bootstrap doctor`
  - check whether the machine and shell state are sane enough to start
- `./tools/bootstrap python`
  - build or refresh the repo-local Python environment
- `source .venv/bin/activate`
  - run the repo tools with the expected Python environment active
- `./tools/python verify`
  - run the normal repo-green verification lane

## What Success Looks Like

Treat these as the normal good signals:

- `./tools/bootstrap doctor`
  - completes without blocking environment errors
- `./tools/bootstrap python`
  - finishes with the repo environment built or refreshed
- `source .venv/bin/activate`
  - returns to the shell without error
- `./tools/python verify`
  - exits successfully
  - does not leave you with a failing pytest summary
  - may classify vendor-specific lanes as blocked or skipped when the host is
    not provisioned, without making the normal repo-green lane fail

If you are unsure whether the verification lane passed, the simplest rule is:

- shell exit success means green for that lane
- a non-zero exit means narrow the failure before rerunning everything

## If You Only Need A Fast First Pass

Use:

```bash
./tools/python verify-fast
```

Use this when:

- you changed docs
- you changed wrappers or light plumbing
- you want a cheap confidence pass before full repo-green

## What "Green" Means Here

For normal local development, green means:

- repo-owned tests and wrappers passed
- the main Python verification lane passed
- vendor-only routes did not silently fail
- blocked vendor prerequisites were classified honestly instead of looking like
  repo regressions

This is the key distinction:

- `repo green`
  - `./tools/python verify`
- `vendor green`
  - `./tools/vendor-green ...`

Do not treat a blocked real vendor runtime as a normal repo failure unless you
were explicitly running the vendor lane.

## If The Default Lane Fails

Use this order:

1. rerun the failing lane directly
2. switch to a focused target
3. rerun the failing file
4. rerun the failing test node

### Step 1: Confirm The Right Lane

Use:

```bash
./tools/test-surface inventory
./tools/test-surface recommend
```

Common lanes:

- `./tools/python verify-fast`
- `./tools/python verify`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes`
- `./tools/python verify-routes-2025`

### Step 2: Use A Focused Target Instead Of Full Reruns

Use:

```bash
./tools/test-focus inventory
./tools/test-focus run foundation
./tools/test-focus run python-examples
./tools/test-focus run java-bridges
./tools/test-focus run target-radar
./tools/test-focus run python-2025-runtime -- --maxfail=1
./tools/test-focus resume python-2025-runtime
```

Use this when:

- full repo-green is too slow
- you already know the failure area
- you need a restartable work loop

### Step 3: Rerun One Failing File

Use:

```bash
./tools/test tests/test_python_route_examples.py
```

### Step 4: Rerun One Failing Test

Use:

```bash
./tools/test tests/test_python_route_examples.py::test_python_route_federate_example_runs_for_supported_editions
```

### Step 5: Rerun By Theme

Use:

```bash
./tools/test -k java_bridge
./tools/test -k python_route
./tools/test -k ownership --lf
```

## Failure Meaning Cheatsheet

### Environment Failure

Typical signal:

- bootstrap fails
- imports are missing
- interpreter or editable install is wrong

Start with:

- [`python_environment.md`](python_environment.md)

### Repo Failure

Typical signal:

- `./tools/python verify` fails in repo-owned tests
- same failure reproduces through `./tools/test` or `./tools/test-focus`

Start with:

- rerun the smallest failing scope
- identify owning package from [`package_layout.md`](package_layout.md)

### Hosted Route Block

Typical signal:

- hosted `grpc` route says blocked
- loopback permission is denied in a managed sandbox

Start with:

```bash
./tools/python verify-routes-preflight
```

Then read:

- [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md)
- [`codex_runner_authorization.md`](codex_runner_authorization.md)

### Vendor Runtime Block

Typical signal:

- CERTI or Pitch preflight is blocked
- Docker or vendor install is unavailable

This does not usually mean repo-green is broken.

Start with:

- [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md)

## Sample Failure Patterns

Use these as rough recognition examples.

### Normal Repo Test Failure

Typical shape:

```text
$ ./tools/python verify
...
FAILED tests/...::test_something
...
= 1 failed, 412 passed ... =
```

Meaning:

- the repo-green lane actually ran
- at least one repo-owned test failed
- narrow to the failing file or node before rerunning the whole lane

Next step:

```bash
./tools/test tests/path/to_file.py
./tools/test tests/path/to_file.py::test_name
```

### Hosted Route Block In A Managed Sandbox

Typical shape:

```text
$ ./tools/python verify-routes-preflight
...
loopback: blocked
python-grpc: blocked
```

Meaning:

- the hosted route is blocked by session or runner policy
- this is not the same thing as a repo regression

Next step:

```bash
./tools/python verify
```

Then, if you specifically need the hosted route:

- read [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md)
- read [`codex_runner_authorization.md`](codex_runner_authorization.md)

### Vendor Runtime Block

Typical shape:

```text
$ ./tools/certi-easy preflight
...
environment: loopback-blocked
```

or:

```text
$ ./tools/pitch preflight
...
environment: docker-blocked
```

Meaning:

- the vendor-specific lane cannot run on this host as currently provisioned
- this does not automatically mean the default repo-green lane is broken

Next step:

```bash
./tools/python verify
```

## When You Need The 2025-Specific Lanes

Use:

```bash
./tools/python verify-main-2025
./tools/python verify-routes-2025
```

Use `verify-main-2025` for the main in-process `python1516_2025` lane.

Use `verify-routes-2025` only when you also need the bounded hosted
`python1516_2025-fedpro-grpc` route lane.

## Best Follow-On Docs

Read these only after the quickstart:

1. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
2. [`test_surface.md`](test_surface.md)
3. [`python_environment.md`](python_environment.md)
4. [`package_layout.md`](package_layout.md)
