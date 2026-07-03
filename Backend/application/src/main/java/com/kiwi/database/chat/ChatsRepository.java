package com.kiwi.database.chat;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ChatsRepository extends JpaRepository<Chats, Integer> {
}
