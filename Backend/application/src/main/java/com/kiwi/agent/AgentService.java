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
import jakarta.transaction.Transactional;
import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.springframework.stereotype.Service;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class AgentService {

    private final TasksRepository tasksRepository;
    private final ChatsRepository chatsRepository;
    private final SlidesRepository slidesRepository;
    private final VersionsRepository versionsRepository;
    private final JsonsRepository jsonsRepository;
    private final ObjectMapper objectMapper;

    public AgentService(TasksRepository tasksRepository,
                        ChatsRepository chatsRepository,
                        SlidesRepository slidesRepository,
                        VersionsRepository versionsRepository,
                        JsonsRepository jsonsRepository,
                        ObjectMapper objectMapper) {
        this.tasksRepository = tasksRepository;
        this.chatsRepository = chatsRepository;
        this.slidesRepository = slidesRepository;
        this.versionsRepository = versionsRepository;
        this.jsonsRepository = jsonsRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public void runTask(Integer taskDBID) {
        Tasks task = tasksRepository.findById(taskDBID).orElse(null);
        if (task == null) {
            return;
        }

        task.setStatus(1);
        tasksRepository.save(task);

        try {
            ProcessBuilder pb = new ProcessBuilder("python",
                    "path/agent.py",
                    "--task_id",
                    String.valueOf(taskDBID));
            pb.redirectErrorStream(true);
            Process process = pb.start();

            String pythonOutput;
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                pythonOutput = reader.lines().collect(Collectors.joining("\n"));
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("Python exit code: " + exitCode + ". Output: " + pythonOutput);
            }

            int jsonStartIndex = pythonOutput.trim().startsWith("[") ? pythonOutput.indexOf('[') : pythonOutput.indexOf('{');
            if (jsonStartIndex != -1) {
                pythonOutput = pythonOutput.substring(jsonStartIndex);
            }

            int type = task.getType();
            Chats chat = task.getChat();

            if (type == 0) {
                List<JsonNode> slidesJson = objectMapper.readValue(pythonOutput, new TypeReference<List<JsonNode>>() {});
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
            else if (type == 1) {
                JsonNode sldieJson = objectMapper.readTree(pythonOutput);
                Versions oldVersion = task.getVersion();

                Versions newVersion = new Versions();
                newVersion.setSlide(oldVersion.getSlide());
                newVersion.setJson(sldieJson.toString());
                versionsRepository.save(newVersion);
            }
            else if (type == 2) {
                Jsons finalJson = new Jsons();
                finalJson.setFile(pythonOutput);
                Jsons savedJson = jsonsRepository.save(finalJson);

                chat.setJson(savedJson);
                chatsRepository.save(chat);
            }

            task.setStatus(2);
            tasksRepository.save(task);


        } catch (Exception e) {
            task.setStatus(3);
            String errorMsg = e.getMessage() != null ? e.getMessage() : "Unknown error";
            task.setErrorMessage(errorMsg.substring(0, Math.min(errorMsg.length(), 250)));
            tasksRepository.save(task);
        }
    }

}
