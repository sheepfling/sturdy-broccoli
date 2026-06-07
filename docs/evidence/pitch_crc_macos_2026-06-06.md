# Pitch CRC macOS Evidence (2026-06-06)

## Raw launcher, bundled Java 11

`python3 scripts/repro_pitch_crc_macos.py`

- `opened_8989 = false`
- `exit_code = 143`

Trace head:

```text
2026-06-06 18:48:39.253 java[75682:4619908] (
    0   CoreFoundation ... __exceptionPreprocess
    1   libobjc.A.dylib ... objc_exception_throw
    2   Foundation ... -[NSMutableDictionary(NSMutableDictionary) initWithContentsOfFile:]
    3   AppKit ... -[NSCGLSurface init]
    4   AppKit ... _NSOpenGLContextGetOffScreenSurface
    5   AppKit ... NSOpenGLContextUpdateOffScreenViewSurface
    10  libawt_lwawt.dylib ... +[GraphicsConfigUtil _getCGLConfigInfo:]
    11  libawt_lwawt.dylib ... Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo
```

## install4j launcher, bundled Java 11

`python3 scripts/repro_pitch_crc_macos.py --launcher-mode install4j`

- `opened_8989 = false`
- `exit_code = 143`

Trace head:

```text
2026-06-06 18:48:39.631 java[75717:4620070] (
    0   CoreFoundation ... __exceptionPreprocess
    1   libobjc.A.dylib ... objc_exception_throw
    2   Foundation ... -[NSMutableDictionary(NSMutableDictionary) initWithContentsOfFile:]
    3   AppKit ... -[NSCGLSurface init]
    4   AppKit ... _NSOpenGLContextGetOffScreenSurface
    5   AppKit ... NSOpenGLContextUpdateOffScreenViewSurface
    10  libawt_lwawt.dylib ... +[GraphicsConfigUtil _getCGLConfigInfo:]
    11  libawt_lwawt.dylib ... Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo
```

## Raw launcher, external Temurin 21

`python3 scripts/repro_pitch_crc_macos.py --java-home /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/jdk4py/java-runtime`

- `opened_8989 = false`
- `exit_code = 1`

Trace head:

```text
2026-06-06 18:48:59.208 java[76149:4620835] (
    0   CoreFoundation ... __exceptionPreprocess
    1   libobjc.A.dylib ... objc_exception_throw
    2   Foundation ... -[NSMutableDictionary(NSMutableDictionary) initWithContentsOfFile:]
    3   AppKit ... -[NSCGLSurface init]
    4   AppKit ... _NSOpenGLContextGetOffScreenSurface
    5   AppKit ... NSOpenGLContextUpdateOffScreenViewSurface
    10  libawt_lwawt.dylib ... __Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo_block_invoke
    11  libawt_lwawt.dylib ... Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo
```

## Conclusion

The launcher path changes the process shape but not the failure signature.
An external JDK changes neither the macOS subsystem involved nor the absence of a listener on `127.0.0.1:8989`.

## Raw launcher, external Homebrew OpenJDK 11

`python3 scripts/repro_pitch_crc_macos.py --java-home /opt/homebrew/opt/openjdk@11`

- `opened_8989 = false`
- `exit_code = 143`

Trace head:

```text
2026-06-06 18:56:00.500 java[7543:4777662] (
    0   CoreFoundation ... __exceptionPreprocess
    1   libobjc.A.dylib ... objc_exception_throw
    2   Foundation ... -[NSMutableDictionary(NSMutableDictionary) initWithContentsOfFile:]
    3   AppKit ... -[NSCGLSurface init]
    4   AppKit ... _NSOpenGLContextGetOffScreenSurface
    5   AppKit ... NSOpenGLContextUpdateOffScreenViewSurface
    10  libawt_lwawt.dylib ... +[GraphicsConfigUtil _getCGLConfigInfo:]
    11  libawt_lwawt.dylib ... Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo
```

## install4j launcher, external Homebrew OpenJDK 11

`python3 scripts/repro_pitch_crc_macos.py --launcher-mode install4j --java-home /opt/homebrew/opt/openjdk@11`

- `opened_8989 = false`
- `exit_code = 143`

Trace head:

```text
2026-06-06 18:56:00.896 java[7576:4777845] (
    0   CoreFoundation ... __exceptionPreprocess
    1   libobjc.A.dylib ... objc_exception_throw
    2   Foundation ... -[NSMutableDictionary(NSMutableDictionary) initWithContentsOfFile:]
    3   AppKit ... -[NSCGLSurface init]
    4   AppKit ... _NSOpenGLContextGetOffScreenSurface
    5   AppKit ... NSOpenGLContextUpdateOffScreenViewSurface
    10  libawt_lwawt.dylib ... +[GraphicsConfigUtil _getCGLConfigInfo:]
    11  libawt_lwawt.dylib ... Java_sun_java2d_opengl_CGLGraphicsConfig_getCGLConfigInfo
```

## Updated conclusion

The launcher path changes neither the failure signature nor the absence of a listener on `127.0.0.1:8989`.
The same macOS AppKit/Java2D OpenGL failure occurs with:

- Pitch bundled Temurin 11
- external Temurin 21
- external Homebrew OpenJDK 11
