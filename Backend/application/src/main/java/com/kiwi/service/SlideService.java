package com.kiwi.service;

import com.kiwi.database.slides.Slides;
import com.kiwi.database.slides.SlidesRepository;
import com.kiwi.database.versions.Versions;
import com.kiwi.dto.response.SlideVersionResponseDto;
import com.kiwi.exception.NotFoundException;
import com.kiwi.util.IdUtil;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.Comparator;

@Service
public class SlideService {

    private final SlidesRepository slidesRepository;
    private final ObjectMapper objectMapper;

    public SlideService(SlidesRepository slidesRepository, ObjectMapper objectMapper) {
        this.slidesRepository = slidesRepository;
        this.objectMapper = objectMapper;
    }

    // GET /chats/{chatID}/slides/{slideID}
    public SlideVersionResponseDto getSlide(String chatID, String slideID) {
        Slides slide = slidesRepository.findBySlideIDAndChat_ChatID(
                IdUtil.parseSlideId(slideID),
                IdUtil.parseChatId(chatID)
        ).orElseThrow(() -> new NotFoundException("Slide not found: " + slideID + " in chat: " + chatID));

        Versions latest = slide.getVersions().stream()
                .max(Comparator.comparing(Versions::getCreatedAt))
                .orElseThrow(() -> new NotFoundException("No versions found for slide: " + slideID));

        return toDto(slideID, latest);
    }

    private SlideVersionResponseDto toDto(String slideID, Versions version) {

        SlideVersionResponseDto dto = new SlideVersionResponseDto();
        dto.setSlideID(slideID);
        dto.setVersionID(IdUtil.versionId(version.getVersionID()));
        dto.setCreatedAt(version.getCreatedAt());

        if (version.getJson() != null) {
            try {
                dto.setSlide(objectMapper.readTree(version.getJson()));
            } catch (Exception e) {
                dto.setSlide(null);
            }
        }

        return dto;
    }

}
