FROM eclipse-temurin:17-jre

LABEL org.opencontainers.image.title="hla-2010 Pitch pRTI Free CRC"
LABEL org.opencontainers.image.vendor="Pitch Technologies"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libxi6 libxtst6 xvfb xdotool \
    && rm -rf /var/lib/apt/lists/*

COPY lib/*.jar /opt/prti1516e/lib/
COPY versioninfo.txt /opt/prti1516e/

WORKDIR /opt/prti1516e

ENV JAVA_OPTS="-XX:+UseParallelGC -XX:MaxRAMPercentage=75"

EXPOSE 8989/tcp
EXPOSE 15164/tcp

CMD ["bash", "-lc", "set -euo pipefail; crc_cp='/opt/prti1516e/lib/prtifull.jar:/opt/prti1516e/lib/booster1516.jar:/opt/prti1516e/lib/webgui2-protocol.jar'; fedpro_cp='/opt/prti1516e/lib/protobuf-java-3.21.7.jar:/opt/prti1516e/lib/*'; Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp & xvfb_pid=$!; export DISPLAY=:99; java $JAVA_OPTS -classpath \"$crc_cp\" se.pitch.prti1516e.RTIexec -nocmdline -nogui -verbose & crc_pid=$!; (set +e; for _ in $(seq 1 30); do for title in 'pRTI License' 'Pitch pRTI Free'; do win=$(xdotool search --name \"$title\" 2>/dev/null | head -1); if [ -n \"$win\" ]; then xdotool windowactivate \"$win\" 2>/dev/null; xdotool mousemove --window \"$win\" 205 325 click 1 2>/dev/null; fi; done; sleep 1; done) & accept_pid=$!; java -Djava.util.logging.config.file=/root/prti1516e/FedProServer.logging -Dse.pitch.prti1516e.useSystemWideLicenseFile=true -Dse.pitch.fedpro.acceptRtiAddressFromClient=true -Dse.pitch.fedpro.acceptAdditionalSettingsFromClient=true -Duser.home=/root -classpath \"$fedpro_cp\" se.pitch.fedpro.server.hla.FedProServerApp & fedpro_pid=$!; trap 'kill $crc_pid $fedpro_pid $accept_pid $xvfb_pid 2>/dev/null || true' TERM INT EXIT; while true; do if ! kill -0 $crc_pid 2>/dev/null; then wait $crc_pid; exit $?; fi; if ! kill -0 $fedpro_pid 2>/dev/null; then wait $fedpro_pid; exit $?; fi; sleep 1; done"]
