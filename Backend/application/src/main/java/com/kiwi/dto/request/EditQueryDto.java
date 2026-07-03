package com.kiwi.dto.request;

import jakarta.validation.constraints.NotBlank;

public class EditQueryDto {

    @NotBlank(message = "prompt is required")
    private String prompt;

    @NotBlank(message = "versionID is required")
    private String versionID;

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public String getVersionID() {
        return versionID;
    }

    public void setVersionID(String versionID) {
        this.versionID = versionID;
    }
}
