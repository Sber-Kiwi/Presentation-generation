package com.kiwi.database.versions;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.slides.SlidesRepository;
import jakarta.persistence.EntityNotFoundException;

import java.time.OffsetDateTime;
import java.util.List;

public class VersionsService {
    private final VersionsRepository versionsRepository;
    private final SlidesRepository slidesRepository;

    public VersionsService(VersionsRepository versionsRepository, SlidesRepository slidesRepository) {
        this.versionsRepository = versionsRepository;
        this.slidesRepository = slidesRepository;
    }

    public List<Versions> getAllVersions() { return versionsRepository.findAll(); }

    public Versions getVersionById(Integer versionId) {
        return versionsRepository.findById(versionId).orElseThrow(() -> new EntityNotFoundException("Version not found " + versionId));
    }

    public List<Versions> getVersionsBySlide(Slides slide) {
        return versionsRepository.findBySlide(slide);
    }

    public List<Versions> getFinalVersions(Integer chatId) {
        return versionsRepository.findBySlide_Chat_ChatIDAndIsFinalTrue(chatId);
    }

    public Versions createVersion (String json, String prompt, OffsetDateTime createdAt, Boolean isFinal, Integer slideId) {
        Slides slide = slidesRepository.findById(slideId).orElseThrow(() -> new EntityNotFoundException("Slide not found " + slideId));

        Versions version = new Versions();
        version.setJson(json);
        version.setPrompt(prompt);
        version.setCreatedAt(createdAt);
        version.setFinal(isFinal);

        return versionsRepository.save(version);
    }

    public Versions updateVersion(Integer versionId, Versions updatedVersion) {
        Versions existing = getVersionById(versionId);
        existing.setJson(updatedVersion.getJson());
        existing.setPrompt(updatedVersion.getPrompt());
        existing.setCreatedAt(updatedVersion.getCreatedAt());
        existing.setFinal(updatedVersion.getFinal());
        return versionsRepository.save(existing);
    }

    public void deleteSlide(Integer versionId) {
        if(!versionsRepository.existsById(versionId)) {
            throw new EntityNotFoundException("Version not found " + versionId);
        }
        versionsRepository.deleteById(versionId);
    }
}
