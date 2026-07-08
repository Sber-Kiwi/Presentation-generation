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

    public AgentSession(String scriptPath, Path csvFilePath) throws IOException {
        this.csvFilePath = csvFilePath;
        
        ProcessBuilder pb = new ProcessBuilder("python3", scriptPath, "--csv_path", csvFilePath.toAbsolutePath().toString());
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
                if (line == null) break;
                
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
                            else if ("rejected".equals(status)) {
                                CompletableFuture<Boolean> f = handshakes.get(taskId);
                                if (f != null) f.complete(false);
                            } 
                            else if ("accepted".equals(status)) {
                                log.debug("Python successfully accepted data for task {}", taskId);
                            }
                        }

                        if (response.has("result")) {
                            CompletableFuture<String> f = pendingResults.get(taskId);
                            if (f != null) {
                                f.complete(line);
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

        while (isRunning) {
            CompletableFuture<Boolean> handshakeFuture = new CompletableFuture<>();
            handshakes.put(taskId, handshakeFuture);
            
            String pingJson = "{\"action\": \"" + action + "\", \"task_id\": " + taskId + "}";
            
            synchronized (writer) {
                writer.write(pingJson + "\n");
                writer.flush();
            }
            log.debug("Sent PING to Python: {}", pingJson);

            boolean accepted = false;
            try {
                accepted = handshakeFuture.get(10, TimeUnit.SECONDS);
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
            String result = resultFuture.get(timeoutSeconds, TimeUnit.SECONDS);
            this.lastActiveTime = System.currentTimeMillis();
            return result;
        } catch (TimeoutException e) {
            pendingResults.remove(taskId);
            log.error("Task {} timed out", taskId);
            throw new RuntimeException("Agent task timed out");
        }
    }

    public long getLastActiveTime() {
        return lastActiveTime;
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