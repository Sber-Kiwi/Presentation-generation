package com.kiwi.api;

import com.kiwi.dto.request.DownloadRequestDto;
import com.kiwi.dto.response.DownloadStatusDto;
import com.kiwi.dto.response.JobResponseDto;
import com.kiwi.service.DownloadService;
import jakarta.validation.Valid;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/chats/{chatID}/downloads")
@CrossOrigin
public class DownloadController {

    private final DownloadService downloadService;

    public DownloadController(DownloadService downloadService) {
        this.downloadService = downloadService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.ACCEPTED)
    public JobResponseDto startExport(@PathVariable String chatID,
                                      @Valid @RequestBody DownloadRequestDto downloadRequestDto) {
        return downloadService.startExport(chatID, downloadRequestDto);
    }

    @GetMapping("/status")
    public DownloadStatusDto getExportStatus(@PathVariable String chatID) {
        return downloadService.getExportStatus(chatID);
    }

    @GetMapping
    public ResponseEntity<byte[]> downloadFile(@PathVariable String chatID) {
        byte[] fileBytes = downloadService.getExportFile(chatID);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.valueOf("application/zip"));
        headers.set(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"presentation.zip\"");

        return new ResponseEntity<>(fileBytes, headers, HttpStatus.OK);
    }

}
