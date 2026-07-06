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
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/chats/{chatID}/slides/{slideID}")
@CrossOrigin
public class SlideController {

    private final SlideService slideService;
    private final EditService editService;
    private final VersionService versionService;
    private final SlideStatusService slideStatusService;

    public SlideController(SlideService slideService,
                           EditService editService,
                           VersionService versionService,
                           SlideStatusService slideStatusService) {
        this.slideService = slideService;
        this.editService = editService;
        this.versionService = versionService;
        this.slideStatusService = slideStatusService;
    }

    @GetMapping
    public SlideVersionResponseDto getSlide(@PathVariable String chatID,
                                            @PathVariable String slideID) {
        return slideService.getSlide(chatID, slideID);
    }

    @PostMapping("/edits")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public JobResponseDto createEdit(@PathVariable String chatID,
                                     @PathVariable String slideID,
                                     @Valid @RequestBody EditQueryDto editQueryDto) {
        return editService.createEdit(chatID, slideID, editQueryDto);
    }

    @GetMapping("/status/{taskID}")
    public SlideStatusDto getSlideStatus(@PathVariable String chatID,
                                         @PathVariable String slideID,
                                         @PathVariable String taskID) {
        return slideStatusService.getSlideStatus(chatID, slideID, taskID);
    }

    @PostMapping("/versions")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public JobResponseDto updateVersion(@PathVariable String chatID,
                                        @PathVariable String slideID,
                                        @Valid @RequestBody SlideVersionDto slideVersionDto) {
        return versionService.updateVersion(chatID, slideID, slideVersionDto);
    }

}
