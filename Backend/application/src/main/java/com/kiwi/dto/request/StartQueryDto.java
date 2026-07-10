package com.kiwi.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.web.multipart.MultipartFile;

public class StartQueryDto {

    @NotBlank(message = "prompt is required")
    @jakarta.validation.constraints.Size(max = 500, message = "Текст запроса не должен превышать 500 символов")
    private String prompt;

    @NotNull(message = "table is required")
    private MultipartFile table;

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public MultipartFile getTable() {
        return table;
    }

    public void setTable(MultipartFile table) {
        this.table = table;
    }
}
