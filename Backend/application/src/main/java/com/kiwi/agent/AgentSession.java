package com.kiwi.agent;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.*;

public class AgentSession {
    private static final Logger log = LoggerFactory.getLogger(AgentSession.class);
    
    private final Process process;
    private final BufferedWriter writer;
    private final BufferedReader reader;
    private final BufferedReader errorReader;
    private final ExecutorService executor;
    private long lastActiveTime;
    private final Path csvFilePath;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private final ConcurrentHashMap<Integer, CompletableFuture<Boolean>> handshakes = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Integer, CompletableFuture<String>> pendingResults = new ConcurrentHashMap<>();
    private final Object slotMonitor = new Object();
    private volatile boolean isRunning = true;
    private final CountDownLatch agentStartedLatch = new CountDownLatch(1);
    private final long startTime;

    private final String mode;

    public AgentSession(String scriptPath, Path csvFilePath, String mode) throws IOException {
        this.csvFilePath = csvFilePath;
        this.mode = mode;
        this.startTime = System.currentTimeMillis();
        ProcessBuilder pb = new ProcessBuilder("python3", "-u", scriptPath, "--file", csvFilePath.toAbsolutePath().toString(), "--mode", mode);
        pb.redirectErrorStream(false); 
        
        this.process = pb.start();
        this.writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8));
        this.reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));
        this.errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8));
        
        this.executor = Executors.newFixedThreadPool(2);
        this.lastActiveTime = System.currentTimeMillis();
        
        // Запускаем фоновые потоки чтения (один для stdout, один для логов stderr)
        this.executor.submit(this::readLoop);
        this.executor.submit(this::errorReadLoop);
        
        log.info("Started new Python AgentSession. PID: {}", process.pid());
    }

    private void readLoop() {
        try {
            while (isRunning) {
                String line = reader.readLine();
                log.info(line);
                if (line == null) break;

                if ("agent started".equals(line.trim())) {
                    long buildTime = System.currentTimeMillis() - startTime;
                    log.info("Agent started successfully. Graph built in {} ms.", buildTime);
                    agentStartedLatch.countDown();
                    continue;
                }
                
                log.debug("Python stdout: {}", line);
                try {
                    JsonNode response = objectMapper.readTree(line);
                    if (response.has("task_id")) {
                        int taskId = response.get("task_id").asInt();

                        if (response.has("status")) {
                            String status = response.get("status").asText();
                            if ("ready".equals(status)) {
                                CompletableFuture<Boolean> f = handshakes.get(taskId);
                                if (f != null) f.complete(true);
                            } 
                            else if ("notready".equals(status)) {
                                CompletableFuture<Boolean> f = handshakes.get(taskId);
                                if (f != null) f.complete(false);
                            } 
                            else if ("accepted".equals(status)) {
                                log.debug("Python successfully accepted data for task {}", taskId);
                            }
                            else if ("rejected".equals(status)) {
                                log.warn("Python rejected the payload for task {}", taskId);
                                CompletableFuture<String> f = pendingResults.get(taskId);
                                if (f != null) {
                                    f.completeExceptionally(new RuntimeException("Task payload was rejected by Python"));
                                    pendingResults.remove(taskId);
                                }
                                synchronized (slotMonitor) {
                                    slotMonitor.notifyAll();
                                }
                            }
                        }

                        if (response.has("output_file")) {
                            CompletableFuture<String> f = pendingResults.get(taskId);
                            if (f != null) {
                                f.complete(response.get("output_file").asText());
                                pendingResults.remove(taskId);
                            }

                            synchronized (slotMonitor) {
                                slotMonitor.notifyAll();
                            }
                        } else if (response.has("error_message")) {
                            CompletableFuture<String> f = pendingResults.get(taskId);
                            if (f != null) {
                                f.completeExceptionally(new RuntimeException(response.get("error_message").asText()));
                                pendingResults.remove(taskId);
                            }

                            synchronized (slotMonitor) {
                                slotMonitor.notifyAll();
                            }
                        }
                    }
                } catch (Exception e) {
                    log.warn("Failed to parse Python JSON line: {}", line);
                }
            }
        } catch (IOException e) {
            if (isRunning) log.error("Error reading from Python process", e);
        } finally {
            failAllPendingFutures("Python process died or stream closed unexpectedly");
        }
    }
    
    private void errorReadLoop() {
        try {
            while (isRunning) {
                String line = errorReader.readLine();
                if (line == null) break;
                log.warn("Python stderr: {}", line);
            }
        } catch (IOException e) {
            if (isRunning) log.error("Error reading stderr from Python", e);
        }
    }

    public String executeWithHandshake(Integer taskId, String action, String fullJsonPayload, long timeoutSeconds) throws Exception {
        this.lastActiveTime = System.currentTimeMillis();

        if (!agentStartedLatch.await(120, TimeUnit.SECONDS)) {
            throw new RuntimeException("Python agent failed to start in time (no 'agent started' message received)");
        }

        while (isRunning) {
            CompletableFuture<Boolean> handshakeFuture = new CompletableFuture<>();
            handshakes.put(taskId, handshakeFuture);
            
            String pingJson = "{\"task_id\": " + taskId + ", \"action\": \"" + action + "\"}";
            log.info("Python handshake request: {}", pingJson);
            
            synchronized (writer) {
                writer.write(pingJson + "\n");
                writer.flush();
            }
            log.debug("Sent PING to Python: {}", pingJson);

            boolean accepted = false;
            try {
                accepted = handshakeFuture.get(60, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                log.warn("Ping timeout for task {}", taskId);
            } finally {
                handshakes.remove(taskId);
            }
            
            if (accepted) {
                break;
            } else {
                log.info("Task {} rejected. Waiting for a free slot...", taskId);
                synchronized (slotMonitor) {
                    slotMonitor.wait(10000); 
                }
            }
        }

        if (!isRunning) throw new RuntimeException("Session closed");

        CompletableFuture<String> resultFuture = new CompletableFuture<>();
        pendingResults.put(taskId, resultFuture);
        
        synchronized (writer) {
            writer.write(fullJsonPayload + "\n");
            writer.flush();
        }
        log.debug("Sent FULL payload for task {}", taskId);

        try {
            String result = resultFuture.get();
            this.lastActiveTime = System.currentTimeMillis();
            return result;
        } catch (Exception e) {
            pendingResults.remove(taskId);
            log.error("Task {} failed: {}", taskId, e.getMessage());
            throw new RuntimeException("Agent task failed: " + e.getMessage());
        }
    }

    private void failAllPendingFutures(String message) {
        RuntimeException ex = new RuntimeException(message);
        for (CompletableFuture<Boolean> f : handshakes.values()) {
            f.completeExceptionally(ex);
        }
        handshakes.clear();
        for (CompletableFuture<String> f : pendingResults.values()) {
            f.completeExceptionally(ex);
        }
        pendingResults.clear();
        synchronized (slotMonitor) {
            slotMonitor.notifyAll();
        }
    }

    public long getLastActiveTime() {
        return lastActiveTime;
    }

    public String getMode() {
        return mode;
    }

    public void close() {
        log.info("Closing AgentSession. PID: {}", process.pid());
        isRunning = false;

        synchronized (slotMonitor) {
            slotMonitor.notifyAll();
        }
        
        try {
            writer.close();
            reader.close();
            errorReader.close();
        } catch (IOException ignored) {}
        
        executor.shutdownNow();
        process.destroyForcibly();
        
        if (csvFilePath != null) {
            try {
                Files.deleteIfExists(csvFilePath);
            } catch (IOException e) {
                log.error("Failed to delete temp CSV: {}", e.getMessage());
            }
        }
    }
}