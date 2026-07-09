FROM eclipse-temurin:25-jdk-jammy AS builder
WORKDIR /app
COPY Backend/application /app/application
WORKDIR /app/application
RUN ./gradlew bootJar --no-daemon
FROM eclipse-temurin:25-jre-jammy

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/application/build/libs/*.jar app.jar

COPY Backend /app/Backend

ENTRYPOINT [ "java", "-jar", "app.jar" ]