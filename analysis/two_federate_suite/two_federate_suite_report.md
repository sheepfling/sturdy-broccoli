# Two-Federate Suite

- suite: `two-federate-suite`
- version: `0.2`
- scenarios: `7`
- track reports: `4`

## Profiles

| Profile | Status | Reason | Scenario rows |
| --- | --- | --- | ---: |
| python | passed |  | 7 |
| certi | skipped | Local socket bind is not permitted for 127.0.0.1. Run `./tools/certi-easy preflight` to verify local CERTI prerequisites. Real RTI smoke needs loopback TCP bind/connect permission for 127.0.0.1. | 0 |
| pitch-jpype | skipped | Runtime process exited early with code 0

pitch crc attempt 1 (raw) diagnostics:
pitch crc attempt 1 (raw) stdout tail:
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch runtime: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch user home: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/pitch/user-home
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch launcher mode: raw
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] launching Pitch via raw java jar

RTIexec for Pitch pRTI(tm) Free v5.5.10 build 9905 for IEEE 1516-2010
Copyright (c) 1998-2024 Pitch Technologies AB, http://www.pitch.se
pitch crc attempt 1 (raw) stderr tail:
	48  libjvm.dylib                        0x000000010dcbc4f4 _ZN9JavaCalls11call_helperEP9JavaValueRK12methodHandleP17JavaCallArgumentsP6Thread + 732
	49  libjvm.dylib                        0x000000010dd06434 _ZL17jni_invoke_staticP7JNIEnv_P9JavaValueP8_jobject11JNICallTypeP10_jmethodIDP18JNI_ArgumentPusherP6Thread + 256
	50  libjvm.dylib                        0x000000010dd0941c jni_CallStaticVoidMethod + 252
	51  libjli.dylib                        0x0000000102fd7920 JavaMain + 1432
	52  libjli.dylib                        0x0000000102fda490 __JVMInit_block_invoke + 72
	53  Foundation                          0x000000018759c16c __NSBLOCKOPERATION_IS_CALLING_OUT_TO_A_BLOCK__ + 24
	54  Foundation                          0x000000018759c03c -[NSBlockOperation main] + 88
	55  Foundation                          0x000000018759bfdc __NSOPERATION_IS_INVOKING_MAIN__ + 16
	56  Foundation                          0x000000018759b3e8 -[NSOperation start] + 640
	57  Foundation                          0x00000001875d6adc __NSThreadPerformPerform + 264
	58  CoreFoundation                      0x0000000185d6ef30 __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 28
	59  CoreFoundation                      0x0000000185d6eec4 __CFRunLoopDoSource0 + 172
	60  CoreFoundation                      0x0000000185d6ec30 __CFRunLoopDoSources0 + 232
	61  CoreFoundation                      0x0000000185d6d854 __CFRunLoopRun + 820
	62  CoreFoundation                      0x0000000185e401c4 _CFRunLoopRunSpecificWithOptions + 532
	63  libjli.dylib                        0x0000000102fd9b08 CreateExecutionEnvironment + 400
	64  libjli.dylib                        0x0000000102fd5f88 JLI_Launch + 1196
	65  java                                0x0000000102f77ba0 main + 396
	66  dyld                                0x00000001858f3e00 start + 6992
)

pitch child 1 attempt 1 (raw) diagnostics:
pitch child 1 attempt 1 (raw) stdout tail:
Pitch pRTI Federate Protocol Server 1.0.
Copyright (c) 2022-2024 Pitch Technologies AB, https://pitchtechnologies.com. All rights reserved.

Server failed to start correctly. Port already in use.
pitch child 1 attempt 1 (raw) stderr tail:
[2026-06-12 06:38:01] [INFO   ] Server is starting. 
[2026-06-12 06:38:01] [SEVERE ] Server failed to start correctly: java.net.BindException: Operation not permitted (Bind failed) 
[2026-06-12 06:38:05] [INFO   ] Server is shutting down.

pitch crc attempt 2 (install4j) diagnostics:
pitch crc attempt 2 (install4j) stdout tail:
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch runtime: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch user home: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/pitch/runtime-homes/launch-81ef2fd19dee485b89061770d825bdc0
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch launcher mode: install4j
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] launching Pitch via install4j cmdline

RTIexec for Pitch pRTI(tm) Free v5.5.10 build 9905 for IEEE 1516-2010
Copyright (c) 1998-2024 Pitch Technologies AB, http://www.pitch.se
pitch crc attempt 2 (install4j) stderr tail:
	60  libjvm.dylib                        0x000000010acbc4f4 _ZN9JavaCalls11call_helperEP9JavaValueRK12methodHandleP17JavaCallArgumentsP6Thread + 732
	61  libjvm.dylib                        0x000000010ad06434 _ZL17jni_invoke_staticP7JNIEnv_P9JavaValueP8_jobject11JNICallTypeP10_jmethodIDP18JNI_ArgumentPusherP6Thread + 256
	62  libjvm.dylib                        0x000000010ad0941c jni_CallStaticVoidMethod + 252
	63  libjli.dylib                        0x00000001004a7920 JavaMain + 1432
	64  libjli.dylib                        0x00000001004aa490 __JVMInit_block_invoke + 72
	65  Foundation                          0x000000018759c16c __NSBLOCKOPERATION_IS_CALLING_OUT_TO_A_BLOCK__ + 24
	66  Foundation                          0x000000018759c03c -[NSBlockOperation main] + 88
	67  Foundation                          0x000000018759bfdc __NSOPERATION_IS_INVOKING_MAIN__ + 16
	68  Foundation                          0x000000018759b3e8 -[NSOperation start] + 640
	69  Foundation                          0x00000001875d6adc __NSThreadPerformPerform + 264
	70  CoreFoundation                      0x0000000185d6ef30 __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 28
	71  CoreFoundation                      0x0000000185d6eec4 __CFRunLoopDoSource0 + 172
	72  CoreFoundation                      0x0000000185d6ec30 __CFRunLoopDoSources0 + 232
	73  CoreFoundation                      0x0000000185d6d854 __CFRunLoopRun + 820
	74  CoreFoundation                      0x0000000185e401c4 _CFRunLoopRunSpecificWithOptions + 532
	75  libjli.dylib                        0x00000001004a9b08 CreateExecutionEnvironment + 400
	76  libjli.dylib                        0x00000001004a5f88 JLI_Launch + 1196
	77  java                                0x0000000100447ba0 main + 396
	78  dyld                                0x00000001858f3e00 start + 6992
)

pitch child 1 attempt 2 (install4j) diagnostics:
pitch child 1 attempt 2 (install4j) stdout tail:
Pitch pRTI Federate Protocol Server 1.0.
Copyright (c) 2022-2024 Pitch Technologies AB, https://pitchtechnologies.com. All rights reserved.

Server failed to start correctly. Port already in use.
pitch child 1 attempt 2 (install4j) stderr tail:
[2026-06-12 06:38:12] [INFO   ] Server is starting. 
[2026-06-12 06:38:12] [SEVERE ] Server failed to start correctly: java.net.BindException: Operation not permitted (Bind failed) 
[2026-06-12 06:38:16] [INFO   ] Server is shutting down. | 0 |
| pitch-py4j | skipped | Runtime process exited early with code 0

pitch crc attempt 1 (raw) diagnostics:
pitch crc attempt 1 (raw) stdout tail:
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch runtime: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch user home: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/pitch/runtime-homes/launch-81ef2fd19dee485b89061770d825bdc0
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch launcher mode: raw
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] launching Pitch via raw java jar

RTIexec for Pitch pRTI(tm) Free v5.5.10 build 9905 for IEEE 1516-2010
Copyright (c) 1998-2024 Pitch Technologies AB, http://www.pitch.se
pitch crc attempt 1 (raw) stderr tail:
	48  libjvm.dylib                        0x000000010ecbc4f4 _ZN9JavaCalls11call_helperEP9JavaValueRK12methodHandleP17JavaCallArgumentsP6Thread + 732
	49  libjvm.dylib                        0x000000010ed06434 _ZL17jni_invoke_staticP7JNIEnv_P9JavaValueP8_jobject11JNICallTypeP10_jmethodIDP18JNI_ArgumentPusherP6Thread + 256
	50  libjvm.dylib                        0x000000010ed0941c jni_CallStaticVoidMethod + 252
	51  libjli.dylib                        0x0000000104457920 JavaMain + 1432
	52  libjli.dylib                        0x000000010445a490 __JVMInit_block_invoke + 72
	53  Foundation                          0x000000018759c16c __NSBLOCKOPERATION_IS_CALLING_OUT_TO_A_BLOCK__ + 24
	54  Foundation                          0x000000018759c03c -[NSBlockOperation main] + 88
	55  Foundation                          0x000000018759bfdc __NSOPERATION_IS_INVOKING_MAIN__ + 16
	56  Foundation                          0x000000018759b3e8 -[NSOperation start] + 640
	57  Foundation                          0x00000001875d6adc __NSThreadPerformPerform + 264
	58  CoreFoundation                      0x0000000185d6ef30 __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 28
	59  CoreFoundation                      0x0000000185d6eec4 __CFRunLoopDoSource0 + 172
	60  CoreFoundation                      0x0000000185d6ec30 __CFRunLoopDoSources0 + 232
	61  CoreFoundation                      0x0000000185d6d854 __CFRunLoopRun + 820
	62  CoreFoundation                      0x0000000185e401c4 _CFRunLoopRunSpecificWithOptions + 532
	63  libjli.dylib                        0x0000000104459b08 CreateExecutionEnvironment + 400
	64  libjli.dylib                        0x0000000104455f88 JLI_Launch + 1196
	65  java                                0x00000001043f7ba0 main + 396
	66  dyld                                0x00000001858f3e00 start + 6992
)

pitch child 1 attempt 1 (raw) diagnostics:
pitch child 1 attempt 1 (raw) stdout tail:
Pitch pRTI Federate Protocol Server 1.0.
Copyright (c) 2022-2024 Pitch Technologies AB, https://pitchtechnologies.com. All rights reserved.

Server failed to start correctly. Port already in use.
pitch child 1 attempt 1 (raw) stderr tail:
[2026-06-12 06:38:22] [INFO   ] Server is starting. 
[2026-06-12 06:38:22] [SEVERE ] Server failed to start correctly: java.net.BindException: Operation not permitted (Bind failed) 
[2026-06-12 06:38:26] [INFO   ] Server is shutting down.

pitch crc attempt 2 (install4j) diagnostics:
pitch crc attempt 2 (install4j) stdout tail:
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch runtime: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch user home: /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/pitch/runtime-homes/launch-0a36aa1a4cd1468f9cd9084ef883b072
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] Pitch launcher mode: install4j
[/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/full_sequence.sh] launching Pitch via install4j cmdline

RTIexec for Pitch pRTI(tm) Free v5.5.10 build 9905 for IEEE 1516-2010
Copyright (c) 1998-2024 Pitch Technologies AB, http://www.pitch.se
pitch crc attempt 2 (install4j) stderr tail:
	60  libjvm.dylib                        0x000000010f4bc4f4 _ZN9JavaCalls11call_helperEP9JavaValueRK12methodHandleP17JavaCallArgumentsP6Thread + 732
	61  libjvm.dylib                        0x000000010f506434 _ZL17jni_invoke_staticP7JNIEnv_P9JavaValueP8_jobject11JNICallTypeP10_jmethodIDP18JNI_ArgumentPusherP6Thread + 256
	62  libjvm.dylib                        0x000000010f50941c jni_CallStaticVoidMethod + 252
	63  libjli.dylib                        0x000000010462b920 JavaMain + 1432
	64  libjli.dylib                        0x000000010462e490 __JVMInit_block_invoke + 72
	65  Foundation                          0x000000018759c16c __NSBLOCKOPERATION_IS_CALLING_OUT_TO_A_BLOCK__ + 24
	66  Foundation                          0x000000018759c03c -[NSBlockOperation main] + 88
	67  Foundation                          0x000000018759bfdc __NSOPERATION_IS_INVOKING_MAIN__ + 16
	68  Foundation                          0x000000018759b3e8 -[NSOperation start] + 640
	69  Foundation                          0x00000001875d6adc __NSThreadPerformPerform + 264
	70  CoreFoundation                      0x0000000185d6ef30 __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 28
	71  CoreFoundation                      0x0000000185d6eec4 __CFRunLoopDoSource0 + 172
	72  CoreFoundation                      0x0000000185d6ec30 __CFRunLoopDoSources0 + 232
	73  CoreFoundation                      0x0000000185d6d854 __CFRunLoopRun + 820
	74  CoreFoundation                      0x0000000185e401c4 _CFRunLoopRunSpecificWithOptions + 532
	75  libjli.dylib                        0x000000010462db08 CreateExecutionEnvironment + 400
	76  libjli.dylib                        0x0000000104629f88 JLI_Launch + 1196
	77  java                                0x00000001045cbba0 main + 396
	78  dyld                                0x00000001858f3e00 start + 6992
)

pitch child 1 attempt 2 (install4j) diagnostics:
pitch child 1 attempt 2 (install4j) stdout tail:
Pitch pRTI Federate Protocol Server 1.0.
Copyright (c) 2022-2024 Pitch Technologies AB, https://pitchtechnologies.com. All rights reserved.

Server failed to start correctly. Port already in use.
pitch child 1 attempt 2 (install4j) stderr tail:
[2026-06-12 06:38:33] [INFO   ] Server is starting. 
[2026-06-12 06:38:33] [SEVERE ] Server failed to start correctly: java.net.BindException: Operation not permitted (Bind failed) 
[2026-06-12 06:38:37] [INFO   ] Server is shutting down. | 0 |

## Coverage

| Scenario | Backend | Callbacks | Key outcome |
| --- | --- | ---: | --- |
| exchange_time | python/in-memory | 13 | receive + timestamp object and interaction delivery |
| synchronization | python/in-memory | 5 | announce and federationSynchronized callbacks |
| ownership | python/in-memory | 6 | divestiture and acquisition if available |
| negotiated_ownership | python/in-memory | 13 | release, cancellation, and reacquisition flow |
| save_restore | python/in-memory | 17 | federationSaved and restore callbacks with restored logical time |
| ddm | python/in-memory | 3 | region-filtered timestamped delivery |
| target_radar | python/in-memory,python/in-memory | 26 | 4 track reports |

## Artifacts

- JSON summary: `two_federate_suite_summary.json`
- Track CSV: `two_federate_track_reports.csv`
- Callback CSV: `two_federate_callbacks.csv`
- SVG summary: `two_federate_suite_summary.svg`
- SVG timeline: `two_federate_suite_timeline.svg`

## Assessment

- A two-federate verification suite exercising exchange, timestamped delivery, synchronization, ownership transfer, negotiated ownership, save/restore, DDM region filtering, and a realistic target/radar flow.
- The default profile runs the Python reference RTI; CERTI and Pitch profiles will record skipped or failed status when their runtimes are unavailable or incomplete.
- The same scenario structure is reused across the python, CERTI, and Pitch runtime profiles.
