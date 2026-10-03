FROM eclipse-temurin:21-jre-jammy@sha256:bce52ea7da1f72e6bf5bec505e63b6eb55ba79ad1226903579f77eab1a80139a
RUN apt-get update && apt-get install --yes --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 loomspan \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin loomspan \
    && mkdir -p /sidecar/data \
    && chown loomspan:loomspan /sidecar/data
WORKDIR /app
COPY runtime-artifacts/sidecar.jar /app/loomspan-sidecar.jar
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:InitialRAMPercentage=25.0 -XX:+ExitOnOutOfMemoryError"
EXPOSE 8080 9091
USER 10001:10001
ENTRYPOINT ["java", "-jar", "/app/loomspan-sidecar.jar"]
HEALTHCHECK --interval=5s --timeout=5s --start-period=60s --retries=12 CMD curl --fail http://localhost:9091/actuator/health/readiness || exit 1
