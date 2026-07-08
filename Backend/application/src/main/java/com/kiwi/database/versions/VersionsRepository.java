package com.kiwi.database.versions;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.slides.Slides;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface VersionsRepository extends JpaRepository<Versions, Integer> {
    List<Versions> findBySlide(Slides slide);

    List<Versions> findBySlide_Chat_ChatIDAndIsFinalTrue (Integer chatId);

    @Query("SELECT v from Versions v WHERE v.createdAt = " +
            "(SELECT MAX(v2.createdAt) FROM Versions v2 WHERE v2.slide.slideID = v.slide.slideID) " +
            "AND v.slide.chat.chatID = :chatId")
    List<Versions> findLatestVersionsByChatId(@Param("chatId") Integer chatID);

    @Query("SELECT v FROM Versions v WHERE v.slide.slideID = :slideId ORDER BY v.createdAt DESC")
    List<Versions> findRecentVersionsBySlideId(@Param("slideId") Integer slideId, Pageable pageable);
}