package com.kiwi.service;

import com.kiwi.agent.AgentService;
import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.dto.request.DownloadRequestDto;
import com.kiwi.dto.response.DownloadStatusDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import com.kiwi.util.StatusUtil;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
public class DownloadService {

    private final ChatsRepository chatsRepository;
    private final TasksRepository tasksRepository;
    private final AgentService agentService;
    private final ObjectMapper objectMapper;

    public DownloadService(ChatsRepository chatsRepository, TasksRepository tasksRepository, AgentService agentService, ObjectMapper objectMapper) {
        this.chatsRepository = chatsRepository;
        this.tasksRepository = tasksRepository;
        this.agentService = agentService;
        this.objectMapper = objectMapper;
    }

    // POST /chats/{chatID}/downloads
    public JobResponseDto startExport(String chatID, DownloadRequestDto dto) {
        Chats chat = chatsRepository.findById(IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID));

        Tasks task = new Tasks();
        task.setChat(chat);
        task.setType(2);
        try {
            String slidesJson = objectMapper.writeValueAsString(dto.getSlides());
            task.setPrompt(slidesJson);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize slides for export", e);
        }
        task.setStatus(0);
        Tasks saved = tasksRepository.save(task);

        agentService.runTask(saved.getTaskID());

        JobResponseDto jobResponseDto = new JobResponseDto();
        jobResponseDto.setChatID(chatID);
        jobResponseDto.setTaskID(IdUtil.taskId(saved.getTaskID()));

        return jobResponseDto;
    }

    // GET /chats/{chatID}/downloads/status
    public DownloadStatusDto getExportStatus(String chatID) {
        Integer chatDBID = IdUtil.parseChatId(chatID);
        if (!chatsRepository.existsById(chatDBID)) {
            throw new NotFoundException("Chat not found: " + chatID);
        }

        Tasks task = tasksRepository.findTopByChat_ChatIDAndTypeOrderByTaskIDDesc(chatDBID, 2)
                .orElseThrow(() -> new NotFoundException("No export jobs found for chat: " + chatID));

        DownloadStatusDto downloadStatusDto = new DownloadStatusDto();
        downloadStatusDto.setStatus(StatusUtil.toApiStatus(task.getStatus()));
        downloadStatusDto.setError(task.getErrorMessage());
        return downloadStatusDto;
    }

    // GET /chats/{chatID}/downloads
    public byte[] getExportFile(String chatID) {
        Integer chatDBID = IdUtil.parseChatId(chatID);
        Chats chat = chatsRepository.findById(chatDBID)
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID));

        if (chat.getJson() == null || chat.getJson().getFile() == null) {
            throw new RuntimeException("Final JSON is not ready yet");
        }
        String finalJson = chat.getJson().getFile();

        try {
            Path tempJsonPath = Files.createTempFile("presentation_", ".json");
            Path tempPptxPath = Files.createTempFile("presentation_", ".pptx");

            Files.writeString(tempJsonPath, finalJson);

            // TODO: paste real path to Python script
            ProcessBuilder pb = new  ProcessBuilder(
                    "python",
                    "path/pptx_generator.py",
                    tempJsonPath.toAbsolutePath().toString(),
                    tempPptxPath.toAbsolutePath().toString()
            );
            pb.redirectErrorStream(true);
            Process process = pb.start();
            int exitCode = process.waitFor();

            if (exitCode != 0) {
                throw new RuntimeException("Python process exited with code " + exitCode);
            }

            byte[] pptxBytes = Files.readAllBytes(tempPptxPath);

            ByteArrayOutputStream baos = new ByteArrayOutputStream();

            try (ZipOutputStream zos = new ZipOutputStream(baos)) {
                ZipEntry pptxEntry = new ZipEntry("presentation.pptx");
                zos.putNextEntry(pptxEntry);
                zos.write(pptxBytes);
                zos.closeEntry();

                ZipEntry jsonEntry = new ZipEntry("presentation.json");
                zos.putNextEntry(jsonEntry);
                zos.write(finalJson.getBytes());
                zos.closeEntry();
            }

            Files.deleteIfExists(tempJsonPath);
            Files.deleteIfExists(tempPptxPath);

            return baos.toByteArray();

        } catch (IOException | InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Failed to generate export archive", e);
        }
    }

}
