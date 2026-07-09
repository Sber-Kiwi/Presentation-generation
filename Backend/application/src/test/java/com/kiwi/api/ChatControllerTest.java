package com.kiwi.api;

import com.kiwi.dto.request.StartQueryDto;
import com.kiwi.dto.response.ChatDto;
import com.kiwi.dto.response.ChatStatusDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.service.ChatService;
import com.kiwi.service.ChatStatusService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(ChatController.class)
public class ChatControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ChatService chatService;

    @MockitoBean
    private ChatStatusService chatStatusService;

    @Test
    public void testCreateChat() throws Exception {
        JobResponseDto mockResponse = new JobResponseDto();
        mockResponse.setChatID("chat_1");
        mockResponse.setTaskID("task_1");

        when(chatService.createChat(any(StartQueryDto.class))).thenReturn(mockResponse);

        MockMultipartFile file = new MockMultipartFile("table", "test.csv", "text/csv", "col1,col2\n1,2".getBytes());

        mockMvc.perform(multipart("/chats")
                        .file(file)
                        .param("prompt", "Create presentation"))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.chatID").value("chat_1"))
                .andExpect(jsonPath("$.taskID").value("task_1"));
    }

    @Test
    public void testGetAllChats() throws Exception {
        com.kiwi.dto.response.ChatSummaryDto summaryDto = new com.kiwi.dto.response.ChatSummaryDto();
        summaryDto.setChatID("chat_1");
        
        when(chatService.getAllChats()).thenReturn(List.of(summaryDto));
        
        mockMvc.perform(get("/chats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].chatID").value("chat_1"));
    }

    @Test
    public void testGetChat() throws Exception {
        ChatDto chatDto = new ChatDto();
        chatDto.setId("chat_1");
        
        when(chatService.getChat("chat_1")).thenReturn(chatDto);

        mockMvc.perform(get("/chats/chat_1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("chat_1"));
    }

    @Test
    public void testGetChatStatus() throws Exception {
        ChatStatusDto statusDto = new ChatStatusDto();
        statusDto.setStatus("processing");

        when(chatStatusService.getChatStatus("chat_1", "task_1")).thenReturn(statusDto);

        mockMvc.perform(get("/chats/chat_1/status/task_1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("processing"));
    }
}
