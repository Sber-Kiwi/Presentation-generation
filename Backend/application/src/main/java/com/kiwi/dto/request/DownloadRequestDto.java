package com.kiwi.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public class DownloadRequestDto {

    @NotNull(message = "slides list is required")
    @Valid
    private List<SlideStateDto> slides;

    private List<EditedSlideDto> editedSlides;

    public List<SlideStateDto> getSlides() {
        return slides;
    }

    public void setSlides(List<SlideStateDto> slides) {
        this.slides = slides;
    }

    public List<EditedSlideDto> getEditedSlides() {
        return editedSlides;
    }

    public void setEditedSlides(List<EditedSlideDto> editedSlides) {
        this.editedSlides = editedSlides;
    }
}
