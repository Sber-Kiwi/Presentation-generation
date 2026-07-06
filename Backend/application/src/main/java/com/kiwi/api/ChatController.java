package com.kiwi.api;

import com.kiwi.dto.request.StartQueryDto;
import com.kiwi.dto.response.ChatDto;
import com.kiwi.dto.response.ChatStatusDto;
import com.kiwi.dto.response.ChatSummaryDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.service.ChatService;
import com.kiwi.service.ChatStatusService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/chats")
@CrossOrigin
public class ChatController {

    private final ChatService chatService;
    private final ChatStatusService chatStatusService;

    public ChatController(ChatService chatService, ChatStatusService chatStatusService) {
        this.chatService = chatService;
        this.chatStatusService = chatStatusService;
    }

    @GetMapping
    public List<ChatSummaryDto> getAllChats() {
        return chatService.getAllChats();
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseStatus(HttpStatus.ACCEPTED)
    public JobResponseDto createChat(@Valid @ModelAttribute StartQueryDto startQueryDto) {
        return chatService.createChat(startQueryDto);
    }

    @GetMapping("/{chatID}/status/{taskID}")
    public ChatStatusDto getChatStatus(@PathVariable String chatID, @PathVariable String taskID) {
        return chatStatusService.getChatStatus(chatID, taskID);
    }

    @GetMapping("/{chatID}")
    public ChatDto getChat(@PathVariable String chatID) {
        return chatService.getChat(chatID);
    }


}
