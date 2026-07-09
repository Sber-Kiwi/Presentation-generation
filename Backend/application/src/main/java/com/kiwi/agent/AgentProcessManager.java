package com.kiwi.agent;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.versions.VersionsRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AgentProcessManager {

    private static final Logger log = LoggerFactory.getLogger(AgentProcessManager.class);

    private static final long SESSION_TIMEOUT_MS = 15 * 60 * 1000;

    private static final String SCRIPT_PATH = System.getenv().getOrDefault(
            "PYTHON_SCRIPT_PATH",
            "/Users/user/study/practice-2026/Presentation-generation/main.py"
    );

    private final ConcurrentHashMap<Integer, AgentSession> sessions = new ConcurrentHashMap<>();

    private final ChatsRepository chatsRepository;
    private final VersionsRepository versionsRepository;
    private final ObjectMapper objectMapper;

    public AgentProcessManager(ChatsRepository chatsRepository, VersionsRepository versionsRepository, ObjectMapper objectMapper) {
        this.chatsRepository = chatsRepository;
        this.versionsRepository = versionsRepository;
        this.objectMapper = objectMapper;
    }

    public AgentSession getSession(Integer chatID, String mode) throws Exception {
        AgentSession session = sessions.get(chatID);

        if (session == null) {
            log.info("Creating new AgentSession for chatID: {} with mode: {}", chatID, mode);

            Chats chat = chatsRepository.findById(chatID).orElse(null);

            if (chat.getCsv() == null || chat.getCsv().getFile() == null) {
                throw new RuntimeException("Critical error: Chat " + chatID + " has no CSV file!");
            }

            Path tempCsvFile = Files.createTempFile("chat_" + chatID + "_", ".csv");
            Files.write(tempCsvFile, chat.getCsv().getFile());

            session = new AgentSession(SCRIPT_PATH, tempCsvFile, mode);
            sessions.put(chatID, session);
        }

        return session;
    }

    @Scheduled(fixedDelay = 60000)
    public void reapInactiveSessions() {
        long now = System.currentTimeMillis();
        for (Map.Entry<Integer, AgentSession> entry : sessions.entrySet()) {
            AgentSession session = entry.getValue();
            if (now - session.getLastActiveTime() > SESSION_TIMEOUT_MS) {
                log.info("Reaping inactive session for chat {}", entry.getKey());
                session.close();
                sessions.remove(entry.getKey());
            }
        }
    }

}
