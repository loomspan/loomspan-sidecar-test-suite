FROM eclipse-temurin:21-jre-jammy@sha256:bce52ea7da1f72e6bf5bec505e63b6eb55ba79ad1226903579f77eab1a80139a
WORKDIR /app
COPY runtime-artifacts/java.jar app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
