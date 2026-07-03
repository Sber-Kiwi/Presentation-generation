package com.kiwi.database.chat;

import com.kiwi.database.csvs.Csvs;
import com.kiwi.database.user.UserRepository;
import com.kiwi.database.user.Users;
import jakarta.persistence.EntityExistsException;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@Service
public class ChatsService {

    private final ChatsRepository chatsRepository;
    private final UserRepository userRepository;

    public ChatsService(ChatsRepository chatsRepository, UserRepository userRepository) {
        this.chatsRepository = chatsRepository;
        this.userRepository = userRepository;
    }

    public List<Chats> getAllChats() {
        return chatsRepository.findAll();
    }

    public Chats addChat(String title, String prompt, Integer userId, MultipartFile csvFile) throws IOException {
        Users user = userRepository.findById(userId).orElseThrow(() -> new EntityNotFoundException("User not found " + userId));

        Chats chat = new Chats();
        chat.setTitle(title);
        chat.setPrompt(prompt);
        chat.setUser(user);

        Csvs csv = new Csvs();
        csv.setFile(csvFile.getBytes());

        chat.setCsv(csv);

        return chatsRepository.save(chat);
    }

}
