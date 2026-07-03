package com.kiwi.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

public class EditedSlideDto {

    @NotNull
    private String slideID;

    @NotNull
    @Valid
    private SlideVersionDto version;

    public String getSlideID() {
        return slideID;
    }

    public void setSlideID(String slideID) {
        this.slideID = slideID;
    }

    public SlideVersionDto getVersion() {
        return version;
    }

    public void setVersion(SlideVersionDto version) {
        this.version = version;
    }
}
