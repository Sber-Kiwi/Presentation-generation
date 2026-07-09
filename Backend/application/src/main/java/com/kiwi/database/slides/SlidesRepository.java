package com.kiwi.database.slides;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.slides.Slides;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.List;

public interface SlidesRepository extends JpaRepository<Slides, Integer> {

    Optional<Slides> findBySlideIDAndChat_ChatID(Integer slideID, Integer chatID);

    List<Slides> findByChat(Chats chat);
}