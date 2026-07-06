package com.kiwi.service;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.slides.SlidesRepository;
import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.database.versions.Versions;
import com.kiwi.database.versions.VersionsRepository;
import com.kiwi.dto.request.EditQueryDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import com.kiwi.util.StatusUtil;
import org.springframework.stereotype.Service;

@Service
public class EditService {

    private final ChatsRepository chatsRepository;
    private final SlidesRepository slidesRepository;
    private final VersionsRepository versionsRepository;
    private final TasksRepository tasksRepository;

    public EditService(ChatsRepository chatsRepository,
                       SlidesRepository slidesRepository,
                       VersionsRepository versionsRepository,
                       TasksRepository tasksRepository) {
        this.chatsRepository = chatsRepository;
        this.slidesRepository = slidesRepository;
        this.versionsRepository = versionsRepository;
        this.tasksRepository = tasksRepository;
    }

    public JobResponseDto createEdit(String chatID, String slideID, EditQueryDto editQueryDto) {
        Chats chat = chatsRepository.findById(IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID));
        Slides slide = slidesRepository.findBySlideIDAndChat_ChatID(
                IdUtil.parseSlideId(slideID),
                IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Slide not found: " + slideID));
        Versions version = versionsRepository.findById(IdUtil.parseVersionId(editQueryDto.getVersionID()))
                .orElseThrow(() -> new NotFoundException("Version not found: " + editQueryDto.getVersionID()));

        Tasks task = new Tasks();
        task.setChat(chat);
        task.setVersion(version);
        task.setPrompt(editQueryDto.getPrompt());
        task.setStatus(0);
        task.setType(1);
        Tasks saved = tasksRepository.save(task);

        // TODO: put python agent to queue

        JobResponseDto jobResponseDto = new JobResponseDto();
        jobResponseDto.setChatID(chatID);
        jobResponseDto.setSlideID(slideID);
        jobResponseDto.setTaskID(IdUtil.taskId(saved.getTaskID()));
        jobResponseDto.setStatus(StatusUtil.toApiStatus(saved.getStatus()));
        return jobResponseDto;
    }

}
