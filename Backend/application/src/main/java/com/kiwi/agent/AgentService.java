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
import com.kiwi.dto.request.SlideStateDto;
import com.kiwi.util.IdUtil;
import jakarta.transaction.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
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
    private final com.kiwi.database.tasks.TasksService tasksService;
    private final ChatsRepository chatsRepository;
    private final SlidesRepository slidesRepository;
    private final VersionsRepository versionsRepository;
    private final JsonsRepository jsonsRepository;
    private final ObjectMapper objectMapper;
    private final AgentProcessManager processManager;

    public AgentService(TasksRepository tasksRepository,
                        com.kiwi.database.tasks.TasksService tasksService,
                        ChatsRepository chatsRepository,
                        SlidesRepository slidesRepository,
                        VersionsRepository versionsRepository,
                        JsonsRepository jsonsRepository,
                        ObjectMapper objectMapper, AgentProcessManager processManager) {
        this.tasksRepository = tasksRepository;
        this.tasksService = tasksService;
        this.chatsRepository = chatsRepository;
        this.slidesRepository = slidesRepository;
        this.versionsRepository = versionsRepository;
        this.jsonsRepository = jsonsRepository;
        this.objectMapper = objectMapper;
        this.processManager = processManager;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void recoverStuckTasks() {
        log.info("Checking for stuck tasks upon application startup...");
        List<Tasks> stuckTasks = tasksRepository.findByStatusIn(List.of(0, 1));
        
        if (stuckTasks.isEmpty()) {
            log.info("No stuck tasks found.");
            return;
        }

        log.info("Found {} stuck task(s). Restarting execution...", stuckTasks.size());
        for (Tasks task : stuckTasks) {
            log.info("Recovering task ID: {}", task.getTaskID());
            task.setStatus(0);
            tasksRepository.save(task);
            new Thread(() -> runTask(task.getTaskID())).start();
        }
    }

    @Async
    @Transactional
    public void runTask(Integer taskDBID) {
        log.info("runTask started for taskDBID: {}", taskDBID);
        Tasks task = tasksRepository.findById(taskDBID).orElse(null);
        if (task == null) {
            log.warn("runTask aborted: task {} not found", taskDBID);
            return;
        }

        tasksService.updateTaskStatus(taskDBID, 1);
        task.setStatus(1); // Update local state for consistency
        Chats chat = task.getChat();

        try {
            String modeStr = task.getType() == 0 ? "start" : "edit";
            AgentSession session = processManager.getSession(chat.getChatID(), modeStr);

            ObjectNode payload = objectMapper.createObjectNode();
            payload.put("task_id", taskDBID);

            Path tempInputFile = null;
            Path tempOutputFile = Files.createTempFile("task_" + taskDBID + "_out_", ".json");
            Path tempCsvFile = null;

            if (task.getType() == 0) {
                payload.put("prompt", chat.getPrompt());
                payload.put("output_file", tempOutputFile.toAbsolutePath().toString());

                if (chat.getCsv() != null && chat.getCsv().getFile() != null) {
                    tempCsvFile = Files.createTempFile("chat_" + chat.getChatID() + "_", ".csv");
                    Files.write(tempCsvFile, chat.getCsv().getFile());
                }
            }
            else if (task.getType() == 1) {
                ObjectNode filePayload = objectMapper.createObjectNode();
                filePayload.put("edit_prompt", task.getPrompt());
                filePayload.set("current_slide", objectMapper.readTree(task.getVersion().getJson()));

                Slides slide = task.getVersion().getSlide();
                List<Versions> recentVersions = versionsRepository.findRecentVersionsBySlideId(slide.getSlideID(),
                        PageRequest.of(0, MAX_RECENT_VERSIONS));

                ArrayNode historyArray = filePayload.putArray("recent_versions_history");
                for (Versions v : recentVersions) {
                    historyArray.add(objectMapper.readTree(v.getJson()));
                }
                
                tempInputFile = Files.createTempFile("task_" + taskDBID + "_in_", ".json");
                Files.writeString(tempInputFile, objectMapper.writeValueAsString(filePayload));
                
                payload.put("input_file", tempInputFile.toAbsolutePath().toString());
                payload.put("output_file", tempOutputFile.toAbsolutePath().toString());

                log.info(filePayload.toString());
            }
            else if (task.getType() == 2) {
                ObjectNode filePayload = objectMapper.createObjectNode();
                JsonNode slidesRequestNode = objectMapper.readTree(task.getPrompt());
                ArrayNode slidesJsonArray = objectMapper.createArrayNode();
                
                if (slidesRequestNode.isArray()) {
                    for (JsonNode slideRequest : slidesRequestNode) {
                        boolean inPresentation = slideRequest.has("inPresentation") && slideRequest.get("inPresentation").asBoolean();
                        if (inPresentation && slideRequest.has("selectedVersionID")) {
                            String versionIdStr = slideRequest.get("selectedVersionID").asText();
                            Integer versionDbId = IdUtil.parseVersionId(versionIdStr);
                            Versions version = versionsRepository.findById(versionDbId).orElse(null);
                            if (version != null) {
                                slidesJsonArray.add(objectMapper.readTree(version.getJson()));
                            }
                        }
                    }
                }
                
                filePayload.set("slides", slidesJsonArray);
                
                tempInputFile = Files.createTempFile("task_" + taskDBID + "_in_", ".json");
                Files.writeString(tempInputFile, objectMapper.writeValueAsString(filePayload));
                
                payload.put("input_file", tempInputFile.toAbsolutePath().toString());
                payload.put("output_file", tempOutputFile.toAbsolutePath().toString());

                log.info(payload.toString());
                log.info(filePayload.toString());
            }

            String actionStr = task.getType() == 0 ? "generate" : (task.getType() == 1 ? "edit" : "export");
            String jsonRequest = objectMapper.writeValueAsString(payload);
            String outputFilePath = session.executeWithHandshake(
                    taskDBID, 
                    actionStr, 
                    jsonRequest, 
                    900
            );

            if (tempCsvFile != null) {
                Files.deleteIfExists(tempCsvFile);
            }
            if (tempInputFile != null) {
                Files.deleteIfExists(tempInputFile);
            }

            String resultFileContent = Files.readString(Path.of(outputFilePath));
            JsonNode resultData = objectMapper.readTree(resultFileContent);

            Files.deleteIfExists(Path.of(outputFilePath));

            if (task.getType() == 0) {
                if (resultData.has("presentation_name") && !resultData.get("presentation_name").isNull()) {
                    String presName = resultData.get("presentation_name").asText();
                    if (presName != null && !presName.trim().isEmpty()) {
                        chat.setTitle(presName);
                        chatsRepository.save(chat);
                    }
                }
                
                JsonNode drafts = resultData.get("drafts");
                if (drafts == null) drafts = resultData; // Fallback just in case
                List<JsonNode> slidesJson = objectMapper.convertValue(drafts, new TypeReference<List<JsonNode>>() {});
                int order = 1;
                for (JsonNode json : slidesJson) {
                    Slides slide = new Slides();
                    slide.setChat(chat);
                    slide.setNum((short) order++);
                    Slides savedSlide = slidesRepository.save(slide);

                    Versions version = new Versions();
                    version.setSlide(savedSlide);
                    version.setJson(json.toString());
                    version.setPrompt("Initial generation");
                    versionsRepository.save(version);
                }
            }
            else if (task.getType() == 1) {
                JsonNode editedSlide = resultData.get("edited_slide");
                if (editedSlide == null) editedSlide = resultData;
                Versions oldVersion = task.getVersion();
                Versions newVersion = new Versions();
                newVersion.setSlide(oldVersion.getSlide());
                newVersion.setJson(editedSlide.toString());
                newVersion.setPrompt(task.getPrompt());
                versionsRepository.save(newVersion);
            }
            else if (task.getType() == 2) {
                JsonNode finalSlidesNode = resultData.get("final_slides");
                if (finalSlidesNode == null) finalSlidesNode = resultData;
                
                ObjectNode finalJsonNode = objectMapper.createObjectNode();
                
                ObjectNode presentationMeta = objectMapper.createObjectNode();
                presentationMeta.put("title", chat.getTitle() != null ? chat.getTitle() : "Презентация");
                presentationMeta.put("common_slide_title", "ПАО Сбербанк. КИБ");
                finalJsonNode.set("meta", presentationMeta);
                
                ArrayNode slidesArray = objectMapper.createArrayNode();
                if (finalSlidesNode.isArray()) {
                    int slideNumber = 1;
                    for (JsonNode slideNode : finalSlidesNode) {
                        if (slideNode.isObject()) {
                            ObjectNode slideObj = (ObjectNode) slideNode;
                            ObjectNode slideMeta = (ObjectNode) slideObj.get("meta");
                            if (slideMeta == null) {
                                slideMeta = objectMapper.createObjectNode();
                                slideObj.set("meta", slideMeta);
                            }
                            
                            if (!slideMeta.has("slide_id")) slideMeta.put("slide_id", "slide_" + slideNumber);
                            if (!slideMeta.has("title")) slideMeta.put("title", "");
                            
                            slideMeta.put("number", slideNumber);
                            slideMeta.put("indicator", "0");
                            
                            if (!slideMeta.has("notes")) slideMeta.putNull("notes");
                            
                            slidesArray.add(slideObj);
                            slideNumber++;
                        }
                    }
                } else if (finalSlidesNode.isObject()) {
                    int slideNumber = 1;
                    Iterable<java.util.Map.Entry<String, JsonNode>> properties = ((ObjectNode) finalSlidesNode).properties();
                    java.util.List<java.util.Map.Entry<String, JsonNode>> entryList = new java.util.ArrayList<>();
                    for (java.util.Map.Entry<String, JsonNode> entry : properties) {
                        entryList.add(entry);
                    }
                    
                    entryList.sort((e1, e2) -> {
                        try {
                            return Integer.compare(Integer.parseInt(e1.getKey()), Integer.parseInt(e2.getKey()));
                        } catch (NumberFormatException ex) {
                            return e1.getKey().compareTo(e2.getKey());
                        }
                    });
                    
                    for (java.util.Map.Entry<String, JsonNode> entry : entryList) {
                        JsonNode slideNode = entry.getValue();
                        if (slideNode.isObject()) {
                            ObjectNode slideObj = (ObjectNode) slideNode;
                            ObjectNode slideMeta = (ObjectNode) slideObj.get("meta");
                            if (slideMeta == null) {
                                slideMeta = objectMapper.createObjectNode();
                                slideObj.set("meta", slideMeta);
                            }
                            
                            if (!slideMeta.has("slide_id")) slideMeta.put("slide_id", "slide_" + slideNumber);
                            if (!slideMeta.has("title")) slideMeta.put("title", "");
                            
                            slideMeta.put("number", slideNumber);
                            slideMeta.put("indicator", "0");
                            
                            if (!slideMeta.has("notes")) slideMeta.putNull("notes");
                            
                            slidesArray.add(slideObj);
                            slideNumber++;
                        }
                    }
                }
                finalJsonNode.set("slides", slidesArray);

                Jsons finalJson = new Jsons();
                finalJson.setFile(finalJsonNode.toString());
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
