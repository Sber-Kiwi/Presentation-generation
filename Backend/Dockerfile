FROM eclipse-temurin:25-jdk-jammy AS builder
WORKDIR /app
COPY Backend/application /app/application
WORKDIR /app/application
RUN --mount=type=cache,target=/root/.gradle \
    ./gradlew bootJar --no-daemon

FROM python:3.14.4-slim

COPY --from=eclipse-temurin:25-jre-jammy /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/application/build/libs/*.jar app.jar

COPY Backend /app/Backend

COPY Backend/LangGraph/.env /app/.env

RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["java", "-jar", "app.jar"]