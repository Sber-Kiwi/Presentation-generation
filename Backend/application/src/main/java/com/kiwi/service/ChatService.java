package com.kiwi.service;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.versions.Versions;
import com.kiwi.dto.request.SlideStateDto;
import com.kiwi.dto.request.SlideVersionDto;
import com.kiwi.dto.request.StartQueryDto;
import com.kiwi.dto.response.ChatDto;
import com.kiwi.dto.response.ChatSummaryDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.dto.response.SlideDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.Comparator;
import java.util.List;

@Service
public class ChatService {

    private final ChatsRepository chatsRepository;
    private final ObjectMapper objectMapper;

    public ChatService(ChatsRepository chatsRepository, ObjectMapper objectMapper) {
        this.chatsRepository = chatsRepository;
        this.objectMapper = objectMapper;
    }

    public List<ChatSummaryDto> getAllChats() {
        return chatsRepository.findAll()
                .stream()
                .map(this::toSummaryDto)
                .toList();
    }

    public ChatDto getChat(String chatID) {
        Chats chat = chatsRepository.findById(IdUtil.parseChatId(chatID))
                .orElseThrow(() -> new NotFoundException("Chat not found: " + chatID ));
        return toDto(chat);
    }

    public JobResponseDto createChat(StartQueryDto startQueryDto) {
        // TODO: realize python agent
        throw new UnsupportedOperationException("Not supported yet!");
    }

    private ChatDto toDto(Chats chat) {
        ChatDto chatDto = new ChatDto();
        chatDto.setId(IdUtil.chatId(chat.getChatID()));
        chatDto.setTitle(chat.getTitle());
        chatDto.setSlides(
                chat.getSlides().stream()
                        .map(this::toSlideDto)
                        .toList()
        );
        return chatDto;
    }

    private SlideDto toSlideDto(Slides slide) {
        SlideDto slideDto = new SlideDto();
        slideDto.setSlideID(IdUtil.slideId(slide.getSlideID()));
        slideDto.setOrder(slide.getNum() != null ? slide.getNum().intValue() : null);
        slideDto.setVersions(slide.getVersions().stream()
                .map(this::toVersionDto)
                .toList());

        slide.getVersions().stream()
                .max(Comparator.comparing(Versions::getCreatedAt))
                .ifPresent(latest -> {
                    SlideStateDto state = new SlideStateDto();
                    state.setSelectedVersionID(IdUtil.versionId(latest.getVersionID()));
                    state.setInPresentation(true);
                    slideDto.setState(state);
                });

        return slideDto;
    }

    private SlideVersionDto toVersionDto(Versions version) {
        SlideVersionDto slideVersionDto = new SlideVersionDto();
        slideVersionDto.setVersionID(IdUtil.versionId(version.getVersionID()));
        slideVersionDto.setCreatedAt(version.getCreatedAt());
        if (version.getJson() != null) {
            try {
                slideVersionDto.setSlide(objectMapper.readTree(version.getJson()));
            } catch (Exception e) {
                slideVersionDto.setSlide(null);
            }
        }
        return slideVersionDto;
    }

    private ChatSummaryDto toSummaryDto(Chats chat) {
        ChatSummaryDto dto = new ChatSummaryDto();
        dto.setChatID(IdUtil.chatId(chat.getChatID()));
        dto.setTitle(chat.getTitle());
        return dto;
    }

}
