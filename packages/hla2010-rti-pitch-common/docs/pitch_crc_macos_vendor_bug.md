# Pitch CRC macOS Vendor Bug

## Summary

On this macOS host, Pitch pRTI Free CRC does not reach a listening state on `127.0.0.1:8989` through either supported launcher path:

- raw jar startup
- Pitch install4j `bin/pRTI cmdline`

The earlier repetitive license-acceptance popup and stale `8989` collision paths were fixed in repo-managed state seeding and launcher cleanup. The remaining failure is a macOS Java/AWT/AppKit startup fault inside Pitch CRC itself.

## Current evidence

- Active Pitch shared settings are normalized before launch:
  - `accepted = true`
  - `CRC.requireWebViewPassPhrase=false`
  - `CRC.webViewPassPhrase=`
- `launch_pitch_runtime()` can now select either launcher path.
- `scripts/run_pitch_local.sh` can now be pointed at an alternate Java runtime with:
  - `HLA2010_PITCH_JAVA_HOME`
  - `HLA2010_PITCH_JAVA_BIN`
  - `HLA2010_PITCH_LAUNCHER_MODE`
  - `HLA2010_PITCH_JVM_ARGS`

## Java runtimes tested

- Pitch bundled Temurin 11.0.22
- External Temurin 21.0.8 from `jdk4py`
- External Homebrew OpenJDK 11.0.31 at `/opt/homebrew/opt/openjdk@11`

Before installation, no non-bundled Java 11 was present on this machine. `openjdk@11` was then installed with Homebrew specifically to complete the external Java 11 comparison.

## Reproducer

Use:

```bash
python3 scripts/repro_pitch_crc_macos.py
```

Install4j path:

```bash
python3 scripts/repro_pitch_crc_macos.py --launcher-mode install4j
```

External JDK:

```bash
python3 scripts/repro_pitch_crc_macos.py \
  --java-home /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/jdk4py/java-runtime
```

The script prints JSON including:

- selected launcher mode
- selected Java runtime
- whether port `8989` opened
- process exit code
- leading stdout/stderr
- crash-report files created during the run

Checked-in run output summary:

- `docs/evidence/pitch_crc_macos_2026-06-06.md`

## Failure signature

Across both bundled Java 11 and external Temurin 21, the stack consistently enters:

- `NSCGLSurface init`
- `_NSOpenGLContextGetOffScreenSurface`
- `Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo`

Representative crash reports observed on June 6, 2026:

- `~/Library/Logs/DiagnosticReports/java-2026-06-06-181738.ips`
- `~/Library/Logs/DiagnosticReports/java-2026-06-06-182637.ips`

## JVM settings tested locally

These did not make CRC reach `127.0.0.1:8989`:

- `-XstartOnFirstThread`
- `-Dsun.java2d.opengl=false`
- `-Dsun.java2d.metal=false`
- `-Dapple.awt.UIElement=true`
- `-Dsun.java2d.pmoffscreen=false`
- `-Dapple.awt.graphics.UseQuartz=true`

`-Djava.awt.headless=true` is not usable because Pitch reports:

`pRTI Free edition does not support running in headless mode.`

## Conclusion

This now looks like a vendor/runtime issue in Pitch CRC on this macOS environment, not a repo integration bug. The external Java 11 comparison is complete and does not change the failure mode. Further work should focus on either:

- running Pitch CRC on Linux/container and using the macOS Java client/FedPro path against it, or
- escalating the reproducer and crash evidence to Pitch as a macOS startup defect.

## Container CRC route

Pitch ships a Linux Docker CRC sample under `third_party/pitch/PITCH-prti1516e-manual/samples/docker`.
The repo now carries a minimal no-WebView variant that uses the installed Pitch Free user-home settings rather
than the sample's floating-license-server settings:

```bash
python3 scripts/repro_pitch_crc_docker.py
```

For the full Pitch backend smoke path, select the Docker CRC mode:

```bash
HLA2010_ENABLE_REAL_RTI_SMOKE=1 \
HLA2010_PITCH_CRC_MODE=docker \
python3 -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k pitch
```

Current local blocker: Docker Desktop starts but has not exposed the Docker daemon socket. Its log shows an
administrator-privilege AppleScript prompt for `vmnetd` configuration, so this path needs an attended macOS
session before the container CRC can be built and tested.
