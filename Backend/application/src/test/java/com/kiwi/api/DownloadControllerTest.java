package com.kiwi.api;

import com.kiwi.dto.request.DownloadRequestDto;
import com.kiwi.dto.request.SlideStateDto;
import com.kiwi.dto.response.DownloadStatusDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.service.DownloadService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.ObjectMapper;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DownloadController.class)
public class DownloadControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private DownloadService downloadService;

    @Test
    public void testStartExport() throws Exception {
        JobResponseDto mockResponse = new JobResponseDto();
        mockResponse.setChatID("chat_1");
        mockResponse.setTaskID("task_1");

        SlideStateDto state = new SlideStateDto();
        state.setSlideID("slide_1");
        state.setSelectedVersionID("version_2");
        state.setInPresentation(true);
        
        DownloadRequestDto request = new DownloadRequestDto();
        request.setSlides(List.of(state));

        when(downloadService.startExport(eq("chat_1"), any(DownloadRequestDto.class)))
                .thenReturn(mockResponse);

        mockMvc.perform(post("/chats/chat_1/downloads")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.taskID").value("task_1"));
    }

    @Test
    public void testGetExportStatus() throws Exception {
        DownloadStatusDto mockResponse = new DownloadStatusDto();
        mockResponse.setStatus("done");

        when(downloadService.getExportStatus("chat_1")).thenReturn(mockResponse);

        mockMvc.perform(get("/chats/chat_1/downloads/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("done"));
    }

    @Test
    public void testGetExportFile() throws Exception {
        byte[] mockZipBytes = "mock-zip-content".getBytes();

        when(downloadService.getExportFile("chat_1")).thenReturn(mockZipBytes);

        mockMvc.perform(get("/chats/chat_1/downloads"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/zip"))
                .andExpect(header().string("Content-Disposition", "attachment; filename=\"presentation.zip\""))
                .andExpect(content().bytes(mockZipBytes));
    }
}
