# Pitch Docker Quickstart

This is the easiest supported path for running the certified HLA 1516-2010
Pitch RTI in this repo.

For the full Pitch decision tree, including Docker vs JPype vs Py4J and the
known quirks, see:

- [Pitch Decision Tree](pitch_decision_tree.md)

## One-time setup

Fastest path:

```bash
./pitch preflight
./pitch all
```

That runs:

- install
- smoke
- verify

If you want the staged flow:

```bash
./pitch install
```

What that does:

- discovers the bundled Pitch runtime under `third_party/pitch/PITCH-prti1516e-manual`
- seeds a persistent Pitch `user.home`
- builds the Docker image used for CRC + FedPro

## Start Pitch

```bash
./pitch start
```

That starts one named container:

- container: `hla2010-pitch-crc`
- CRC: `127.0.0.1:8989`
- FedPro: `127.0.0.1:15164`

## Smoke test

```bash
./pitch smoke
```

## Full real Pitch matrix

```bash
./pitch verify
```

## Day-to-day commands

```bash
./pitch status
./pitch logs
./pitch stop
./pitch restart
./pitch doctor
./pitch all
```

## Zero-thinking vendor smoke

If you just want the standard vendor smoke wrapper, this now works with
repo-local Pitch defaults:

```bash
./scripts/ci/vendor_green.sh pitch
```

## If it fails

Use:

```bash
./pitch preflight
./pitch doctor
./pitch logs
```

Common causes:

- Docker Desktop is not running
- the Pitch runtime bundle is missing from `third_party/pitch/PITCH-prti1516e-manual`
- another process is already bound to `8989` or `15164`

If you prefer the explicit script path, `./pitch` is a thin alias for
`./pitch`.
