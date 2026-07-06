package com.kiwi.database.chat;

import com.kiwi.database.csvs.CsvsService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/v1/database/chats")
public class ChatsController {

    private final ChatsService chatsService;


    public ChatsController(ChatsService chatsService) {
        this.chatsService = chatsService;
    }

    @GetMapping
    public List<Chats> getChats() {
        return  chatsService.getAllChats();
    }

    @PostMapping(consumes = "multipart/form-data")
    public ResponseEntity<Chats> addChat(@RequestParam String title,
                                         @RequestParam String prompt,
                                         @RequestParam Integer userId,
                                         @RequestParam MultipartFile csvFile
                                         ) throws IOException {
        Chats saved = chatsService.createChat(title, prompt, userId, csvFile);
        return ResponseEntity.ok(saved);
    }

}
