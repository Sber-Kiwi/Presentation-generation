package com.kiwi.service;

import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.dto.response.ChatStatusDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import com.kiwi.util.StatusUtil;
import org.hibernate.annotations.NotFound;
import org.springframework.stereotype.Service;

@Service
public class ChatStatusService {

    private final TasksRepository tasksRepository;

    public ChatStatusService(TasksRepository tasksRepository) {
        this.tasksRepository = tasksRepository;
    }

    public ChatStatusDto getChatStatus(String chatID, String taskID) {
        Tasks task = tasksRepository.findById(IdUtil.parseTaskId(taskID))
                .orElseThrow(() -> new NotFoundException("Task nor found: " + taskID));
        if (!task.getChat().getChatID().equals(IdUtil.parseChatId(chatID))) {
            throw new NotFoundException("Task " + taskID + " not found in chat: " + chatID);
        }

        ChatStatusDto chatStatusDto = new ChatStatusDto();
        chatStatusDto.setStatus(StatusUtil.toApiStatus(task.getStatus()));
        chatStatusDto.setError(task.getErrorMessage());
        return chatStatusDto;
    }

}
