package com.kiwi.database.chat;

import com.kiwi.database.csvs.Csvs;
import com.kiwi.database.csvs.CsvsRepository;
import com.kiwi.database.jsons.JsonsRepository;
import com.kiwi.database.user.UsersRepository;
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
    private final UsersRepository usersRepository;
    private final CsvsRepository csvsRepository;
    private final JsonsRepository jsonsRepository;

    public ChatsService(ChatsRepository chatsRepository, UsersRepository usersRepository,
                        CsvsRepository csvsRepository, JsonsRepository jsonsRepository) {
        this.chatsRepository = chatsRepository;
        this.usersRepository = usersRepository;
        this.csvsRepository = csvsRepository;
        this.jsonsRepository = jsonsRepository;
    }

    public List<Chats> getAllChats() {
        return chatsRepository.findAll();
    }

    public Chats getChatById(Integer chatId) {
        return chatsRepository.findById(chatId).orElseThrow(() -> new EntityNotFoundException("Chat not found " + chatId));
    }

    public Chats createChat(String title, String prompt, Integer userId, MultipartFile csvFile) throws IOException {
        Users user = usersRepository.findById(userId).orElseThrow(() -> new EntityNotFoundException("User not found " + userId));

        Chats chat = new Chats();
        chat.setTitle(title);
        chat.setPrompt(prompt);
        chat.setUser(user);

        Csvs csv = new Csvs();
        csv.setFile(csvFile.getBytes());

        chat.setCsv(csv);

        return chatsRepository.save(chat);
    }

    public void deleteChat(Integer chatId) {
        if(!chatsRepository.existsById(chatId)) {
            throw new EntityNotFoundException("Chat not found " + chatId);
        }
    }
}
