package com.kiwi.dto.request;

import jakarta.validation.constraints.NotNull;
import tools.jackson.databind.JsonNode;

import java.time.OffsetDateTime;

public class SlideVersionDto {

    private String versionID;

    @NotNull(message = "slide draft is required")
    private JsonNode slide;

    private OffsetDateTime createdAt;

    public String getVersionID() {
        return versionID;
    }

    public void setVersionID(String versionID) {
        this.versionID = versionID;
    }

    public JsonNode getSlide() {
        return slide;
    }

    public void setSlide(JsonNode slide) {
        this.slide = slide;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
