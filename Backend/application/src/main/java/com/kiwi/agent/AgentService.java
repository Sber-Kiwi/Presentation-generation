package com.kiwi.agent;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.jsons.Jsons;
import com.kiwi.database.jsons.JsonsRepository;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.slides.SlidesRepository;
import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.database.versions.Versions;
import com.kiwi.database.versions.VersionsRepository;
import com.kiwi.util.IdUtil;
import jakarta.transaction.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.ArrayNode;
import tools.jackson.databind.node.ObjectNode;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Service
public class AgentService {

    private static final int MAX_RECENT_VERSIONS = 2;
    private static final Logger log = LoggerFactory.getLogger(AgentService.class);

    private final TasksRepository tasksRepository;
    private final ChatsRepository chatsRepository;
    private final SlidesRepository slidesRepository;
    private final VersionsRepository versionsRepository;
    private final JsonsRepository jsonsRepository;
    private final ObjectMapper objectMapper;
    private final AgentProcessManager processManager;

    public AgentService(TasksRepository tasksRepository,
                        ChatsRepository chatsRepository,
                        SlidesRepository slidesRepository,
                        VersionsRepository versionsRepository,
                        JsonsRepository jsonsRepository,
                        ObjectMapper objectMapper, AgentProcessManager processManager) {
        this.tasksRepository = tasksRepository;
        this.chatsRepository = chatsRepository;
        this.slidesRepository = slidesRepository;
        this.versionsRepository = versionsRepository;
        this.jsonsRepository = jsonsRepository;
        this.objectMapper = objectMapper;
        this.processManager = processManager;
    }

    @Async
    @Transactional
    public void runTask(Integer taskDBID) {
        Tasks task = tasksRepository.findById(taskDBID).orElse(null);
        if (task == null) {
            return;
        }

        task.setStatus(1);
        tasksRepository.save(task);
        Chats chat = task.getChat();

        try {
            AgentSession session = processManager.getSession(chat.getChatID());

            ObjectNode payload = objectMapper.createObjectNode();
            payload.put("task_id", taskDBID);
            payload.put("chat_id", chat.getChatID());

            Path tempCsvFile = null;

            if (task.getType() == 0) {
                payload.put("action", "generate");
                payload.put("prompt", chat.getPrompt());

                if (chat.getCsv() != null && chat.getCsv().getFile() != null) {
                    tempCsvFile = Files.createTempFile("chat_" + chat.getChatID() + "_", ".csv");
                    Files.write(tempCsvFile, chat.getCsv().getFile());
                }

            }
            else if (task.getType() == 1) {
                payload.put("action", "edit");
                payload.put("edit_prompt", task.getPrompt());
                payload.set("current_slide", objectMapper.readTree(task.getVersion().getJson()));

                Slides slide = task.getVersion().getSlide();
                List<Versions> recentVersions = versionsRepository.findRecentVersionsBySlideId(slide.getSlideID(),
                        PageRequest.of(0, MAX_RECENT_VERSIONS));

                ArrayNode historyArray = payload.putArray("recent_versions_history");
                for (Versions v : recentVersions) {
                    ObjectNode vNode = objectMapper.createObjectNode();
                    vNode.put("versionID", IdUtil.versionId(v.getVersionID()));
                    vNode.set("json", objectMapper.readTree(v.getJson()));

                    if (v.getPrompt() != null) {
                        vNode.put("prompt", v.getPrompt());
                    }

                    historyArray.add(vNode);
                }
            }
            else if (task.getType() == 2) {
                payload.put("action", "export");
                payload.set("slides", objectMapper.readTree(task.getPrompt()));
            }

            String jsonRequest = objectMapper.writeValueAsString(payload);
            String pythonOutput = session.executeWithHandshake(
                    taskDBID, 
                    payload.get("action").asText(), 
                    jsonRequest, 
                    300
            );

            if (tempCsvFile != null) {
                Files.deleteIfExists(tempCsvFile);
            }

            JsonNode responseNode = objectMapper.readTree(pythonOutput);
            JsonNode resultData = responseNode.get("result");

            if (responseNode.has("status") && "error".equals(responseNode.get("status").asText())) {
                throw new RuntimeException("Python error: " + responseNode.get("message").asText());
            }

            if (task.getType() == 0) {
                List<JsonNode> slidesJson = objectMapper.convertValue(resultData, new TypeReference<List<JsonNode>>() {});
                int order = 1;
                for (JsonNode json : slidesJson) {
                    Slides slide = new Slides();
                    slide.setChat(chat);
                    slide.setNum((short) order++);
                    Slides savedSlide = slidesRepository.save(slide);

                    Versions version = new Versions();
                    version.setSlide(savedSlide);
                    version.setJson(json.toString());
                    versionsRepository.save(version);
                }
            }
            else if (task.getType() == 1) {
                Versions oldVersion = task.getVersion();
                Versions newVersion = new Versions();
                newVersion.setSlide(oldVersion.getSlide());
                newVersion.setJson(resultData.toString());
                versionsRepository.save(newVersion);
            }
            else if (task.getType() == 2) {
                Jsons finalJson = new Jsons();
                finalJson.setFile(resultData.asText());
                Jsons savedJson = jsonsRepository.save(finalJson);

                chat.setJson(savedJson);
                chatsRepository.save(chat);
            }

            task.setStatus(2);
            tasksRepository.save(task);
        } catch (Exception e) {
            log.error("Task {} failed: {}", taskDBID, e.getMessage());
            task.setStatus(3);
            String errorMsg = e.getMessage() != null ? e.getMessage() : "Unknown error";
            task.setErrorMessage(errorMsg.substring(0, Math.min(errorMsg.length(), 250)));
            tasksRepository.save(task);
        }

    }

}
