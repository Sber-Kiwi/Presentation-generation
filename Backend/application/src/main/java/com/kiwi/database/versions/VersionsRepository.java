package com.kiwi.database.versions;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.slides.Slides;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface VersionsRepository extends JpaRepository<Versions, Integer> {
    List<Versions> findBySlide(Slides slide);

    List<Versions> findBySlide_Chat_ChatIDAndIsFinalTrue (Integer chatId);
}