package com.kiwi.database.slides;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SlidesRepository extends JpaRepository<Slides, Integer> {
    Optional<Slides> findBySlideIDAndChat_ChatID(Integer slideID, Integer chatID);
}
