package com.kiwi.dto.response;

import java.util.List;

public class ChatDto {

    private String id;
    private String title;
    private List<SlideDto> slides;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public List<SlideDto> getSlides() {
        return slides;
    }

    public void setSlides(List<SlideDto> slides) {
        this.slides = slides;
    }
}
