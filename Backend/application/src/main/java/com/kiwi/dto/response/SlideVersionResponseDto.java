package com.kiwi.dto.response;

import tools.jackson.databind.JsonNode;

import java.time.OffsetDateTime;

public class SlideVersionResponseDto {

    private String slideID;
    private String versionID;
    private JsonNode slide;
    private OffsetDateTime createdAt;

    public String getSlideID() {
        return slideID;
    }

    public void setSlideID(String slideID) {
        this.slideID = slideID;
    }

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
