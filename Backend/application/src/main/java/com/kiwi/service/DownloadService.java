package com.kiwi.service;

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

@Service
public class DownloadService {

    private final ChatsRepository chatsRepository;
    private final TasksRepository tasksRepository;

    public DownloadService(ChatsRepository chatsRepository, TasksRepository tasksRepository) {
        this.chatsRepository = chatsRepository;
        this.tasksRepository = tasksRepository;
    }

    // POST /chats/{chatID}/downloads
    public JobResponseDto startExport(String chatID, DownloadRequestDto dto) {
        Chats chat = chatsRepository.findById(IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID));

        Tasks task = new Tasks();
        task.setChat(chat);
        task.setType(2);
        task.setPrompt("Export to PPTX"); // заглушка
        task.setStatus(0);
        Tasks saved = tasksRepository.save(task);

        // TODO: send task to python-agent

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
        throw new UnsupportedOperationException("File download is not yet implemented");
    }

}
