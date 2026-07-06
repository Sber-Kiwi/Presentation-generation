package com.kiwi.service;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.slides.SlidesRepository;
import com.kiwi.database.tasks.TasksRepository;
import com.kiwi.database.versions.Versions;
import com.kiwi.database.versions.VersionsRepository;
import com.kiwi.dto.request.SlideVersionDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import org.springframework.stereotype.Service;

@Service
public class VersionService {

    private final ChatsRepository chatsRepository;
    private final SlidesRepository slidesRepository;
    private final VersionsRepository versionsRepository;
    private final TasksRepository tasksRepository;

    public VersionService(ChatsRepository chatsRepository, SlidesRepository slidesRepository, VersionsRepository versionsRepository, TasksRepository tasksRepository) {
        this.chatsRepository = chatsRepository;
        this.slidesRepository = slidesRepository;
        this.versionsRepository = versionsRepository;
        this.tasksRepository = tasksRepository;
    }

    public JobResponseDto updateVersion(String chatID, String slideID, SlideVersionDto dto) {
        Chats chat = chatsRepository.findById(IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID));
        Slides slide = slidesRepository.findBySlideIDAndChat_ChatID(
                IdUtil.parseSlideId(slideID),
                IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Slide not found: " +  slideID));

        Versions version = versionsRepository.findById(IdUtil.parseVersionId(dto.getVersionID()))
                .orElseThrow(() -> new NotFoundException("Version not found: " + dto.getVersionID()));

        if (dto.getSlide() != null) {
            version.setJson(dto.getSlide().toString());
            versionsRepository.save(version);
        }

        JobResponseDto response = new JobResponseDto();
        response.setChatID(chatID);
        response.setTaskID(null);

        return response;
    }

}
