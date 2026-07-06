package com.kiwi.service;

import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.database.versions.Versions;
import com.kiwi.dto.response.SlideStatusDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import com.kiwi.util.StatusUtil;
import org.springframework.stereotype.Service;

import java.util.Comparator;

@Service
public class SlideStatusService {
    
    private final TasksRepository tasksRepository;

    public SlideStatusService(TasksRepository tasksRepository) {
        this.tasksRepository = tasksRepository;
    }
    
    public SlideStatusDto getSlideStatus(String chatID, String slideID, String taskID) {
        Tasks task = tasksRepository.findById(IdUtil.parseTaskId(taskID))
                .orElseThrow(() -> new NotFoundException("Task not found: " + taskID));
        
        if (!task.getChat().getChatID().equals(IdUtil.parseChatId(chatID))) {
            throw new NotFoundException("Task " + taskID + " not found in chat: " + chatID);
        }
        
        SlideStatusDto dto = new SlideStatusDto();
        dto.setStatus(StatusUtil.toApiStatus(task.getStatus()));
        dto.setError(task.getErrorMessage());
        
        if (task.getStatus() == 2 && task.getVersion() != null) {
            task.getVersion().getSlide().getVersions().stream()
                    .max(Comparator.comparing(Versions::getCreatedAt))
                    .ifPresent(latestVersion -> dto.setNewVersionID(IdUtil.versionId(latestVersion.getVersionID())));
        }

        return dto;
    }
    
}
