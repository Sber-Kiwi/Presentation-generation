import com.kiwi.agent.AgentSession;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TestHandshake {
    public static void main(String[] args) throws Exception {
        System.out.println("=== STARTING HANDSHAKE TEST ===");
        
        // Создаем временный CSV файл (заглушка)
        Path tempCsv = Files.createTempFile("test_", ".csv");
        
        // Создаем сессию, указывая на наш мок Питона
        AgentSession session = new AgentSession("/Users/user/study/practice-2026/Presentation-generation/mock_main.py", tempCsv);
        
        // Запускаем 5 одновременных задач (имитация 5 пользователей или 5 кликов)
        ExecutorService executor = Executors.newFixedThreadPool(5);
        
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                try {
                    System.out.println("Thread " + taskId + " started.");
                    String result = session.executeWithHandshake(
                        taskId, 
                        "edit", 
                        "{\"data\": \"huge_payload_for_task_" + taskId + "\"}", 
                        30
                    );
                    System.out.println(">>> SUCCESS! Task " + taskId + " finished with result: " + result);
                } catch (Exception e) {
                    System.err.println("Task " + taskId + " failed: " + e.getMessage());
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(30, TimeUnit.SECONDS);
        session.close();
        System.out.println("=== TEST FINISHED ===");
    }
}
