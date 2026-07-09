package com.kiwi.api;

import com.kiwi.dto.request.EditQueryDto;
import com.kiwi.dto.request.SlideVersionDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.dto.response.SlideStatusDto;
import com.kiwi.dto.response.SlideVersionResponseDto;
import com.kiwi.service.EditService;
import com.kiwi.service.SlideService;
import com.kiwi.service.SlideStatusService;
import com.kiwi.service.VersionService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.ObjectMapper;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(SlideController.class)
public class SlideControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private SlideService slideService;

    @MockitoBean
    private EditService editService;

    @MockitoBean
    private SlideStatusService slideStatusService;

    @MockitoBean
    private VersionService versionService;

    @Test
    public void testGetSlide() throws Exception {
        SlideVersionResponseDto mockResponse = new SlideVersionResponseDto();
        mockResponse.setSlideID("slide_1");
        mockResponse.setVersionID("version_1");

        when(slideService.getSlide("chat_1", "slide_1")).thenReturn(mockResponse);

        mockMvc.perform(get("/chats/chat_1/slides/slide_1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.slideID").value("slide_1"))
                .andExpect(jsonPath("$.versionID").value("version_1"));
    }

    @Test
    public void testCreateEdit() throws Exception {
        JobResponseDto mockResponse = new JobResponseDto();
        mockResponse.setChatID("chat_1");
        mockResponse.setTaskID("task_1");

        EditQueryDto request = new EditQueryDto();
        request.setPrompt("Make it red");
        request.setVersionID("version_1");

        when(editService.createEdit(eq("chat_1"), eq("slide_1"), any(EditQueryDto.class)))
                .thenReturn(mockResponse);

        mockMvc.perform(post("/chats/chat_1/slides/slide_1/edits")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.taskID").value("task_1"));
    }

    @Test
    public void testGetEditStatus() throws Exception {
        SlideStatusDto mockResponse = new SlideStatusDto();
        mockResponse.setStatus("processing");

        when(slideStatusService.getSlideStatus("chat_1", "slide_1", "task_1"))
                .thenReturn(mockResponse);

        mockMvc.perform(get("/chats/chat_1/slides/slide_1/status/task_1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("processing"));
    }

    @Test
    public void testCreateVersion() throws Exception {
        JobResponseDto mockResponse = new JobResponseDto();
        mockResponse.setChatID("chat_1");

        SlideVersionDto request = new SlideVersionDto();
        request.setVersionID("version_1");

        when(versionService.updateVersion(eq("chat_1"), eq("slide_1"), any(SlideVersionDto.class)))
                .thenReturn(mockResponse);

        mockMvc.perform(post("/chats/chat_1/slides/slide_1/versions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.chatID").value("chat_1"));
    }
}
